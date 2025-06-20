from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from models import PaymentTransaction, PaymentTransactionCreate, SubscriptionPlan, PaymentStatus
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Stripe Configuration
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

# Payment Plans Configuration
PAYMENT_PLANS = {
    SubscriptionPlan.BASIC: {
        "amount": 100000.0,  # 100,000 FRW
        "currency": "FRW",
        "survey_limit": 4,
        "storage_limit": 1.0,  # 1 GB
        "features": [
            "4 active surveys",
            "1 GB data storage",
            "Basic analytics",
            "Email support",
            "Data export (CSV)"
        ]
    },
    SubscriptionPlan.PROFESSIONAL: {
        "amount": 300000.0,  # 300,000 FRW
        "currency": "FRW", 
        "survey_limit": 10,
        "storage_limit": 3.0,  # 3 GB
        "features": [
            "10 active surveys",
            "3 GB data storage",
            "Advanced analytics",
            "Priority support", 
            "Multiple export formats",
            "Skip logic & calculations",
            "Custom branding"
        ]
    },
    SubscriptionPlan.ENTERPRISE: {
        "amount": None,  # Custom pricing
        "currency": "FRW",
        "survey_limit": -1,  # Unlimited
        "storage_limit": -1.0,  # Unlimited
        "features": [
            "Unlimited surveys",
            "Unlimited storage",
            "Advanced KPI dashboards",
            "24/7 dedicated support",
            "API access",
            "White-label solution",
            "Custom integrations",
            "Advanced user management"
        ]
    }
}

class PaymentService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        if STRIPE_API_KEY:
            self.stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        else:
            self.stripe_checkout = None
            logger.warning("Stripe API key not configured")

    async def create_checkout_session(
        self,
        organization_id: str,
        plan: SubscriptionPlan,
        user_id: Optional[str],
        origin_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CheckoutSessionResponse:
        """Create a Stripe checkout session for a subscription plan"""
        
        if not self.stripe_checkout:
            raise ValueError("Stripe not configured")
        
        # Get plan configuration
        plan_config = PAYMENT_PLANS.get(plan)
        if not plan_config:
            raise ValueError(f"Invalid plan: {plan}")
        
        if plan == SubscriptionPlan.ENTERPRISE:
            raise ValueError("Enterprise plans require custom pricing")
        
        # Build success and cancel URLs
        success_url = f"{origin_url}/dashboard?payment_success=true&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/dashboard?payment_cancelled=true"
        
        # Prepare metadata
        session_metadata = {
            "organization_id": organization_id,
            "plan": plan.value,
            "user_id": user_id or "",
            **(metadata or {})
        }
        
        # Create checkout session request
        checkout_request = CheckoutSessionRequest(
            amount=plan_config["amount"],
            currency=plan_config["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=session_metadata
        )
        
        # Create checkout session with Stripe
        session = await self.stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction in database
        payment_transaction = PaymentTransactionCreate(
            organization_id=organization_id,
            user_id=user_id,
            stripe_session_id=session.session_id,
            amount=plan_config["amount"],
            currency=plan_config["currency"],
            plan=plan,
            metadata=session_metadata
        )
        
        payment_doc = PaymentTransaction(**payment_transaction.dict())
        await self.db.payment_transactions.insert_one(payment_doc.dict(by_alias=True))
        
        logger.info(f"Created checkout session {session.session_id} for organization {organization_id}")
        return session

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        """Get the status of a checkout session"""
        
        if not self.stripe_checkout:
            raise ValueError("Stripe not configured")
        
        # Get status from Stripe
        status_response = await self.stripe_checkout.get_checkout_status(session_id)
        
        # Update payment transaction in database
        payment_transaction = await self.db.payment_transactions.find_one(
            {"stripe_session_id": session_id}
        )
        
        if payment_transaction:
            update_data = {
                "payment_status": self._map_stripe_status(status_response.payment_status),
                "updated_at": datetime.utcnow()
            }
            
            # If payment successful and not already processed
            if (status_response.payment_status == "paid" and 
                payment_transaction.get("payment_status") != PaymentStatus.PAID):
                
                # Update organization subscription
                await self._update_organization_subscription(
                    payment_transaction["organization_id"],
                    payment_transaction["plan"]
                )
                
                logger.info(f"Payment successful for session {session_id}")
            
            await self.db.payment_transactions.update_one(
                {"stripe_session_id": session_id},
                {"$set": update_data}
            )
        
        return status_response

    def _map_stripe_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe payment status to our PaymentStatus enum"""
        mapping = {
            "paid": PaymentStatus.PAID,
            "unpaid": PaymentStatus.PENDING,
            "no_payment_required": PaymentStatus.PAID,
            "failed": PaymentStatus.FAILED
        }
        return mapping.get(stripe_status, PaymentStatus.PENDING)

    async def _update_organization_subscription(self, organization_id: str, plan: SubscriptionPlan):
        """Update organization subscription after successful payment"""
        
        plan_config = PAYMENT_PLANS.get(plan)
        if not plan_config:
            return
        
        update_data = {
            "plan": plan.value,
            "survey_limit": plan_config["survey_limit"],
            "storage_limit": plan_config["storage_limit"],
            "updated_at": datetime.utcnow()
        }
        
        await self.db.organizations.update_one(
            {"_id": organization_id},
            {"$set": update_data}
        )
        
        logger.info(f"Updated organization {organization_id} to {plan.value} plan")

    async def get_payment_history(self, organization_id: str) -> List[PaymentTransaction]:
        """Get payment history for an organization"""
        
        payments = await self.db.payment_transactions.find(
            {"organization_id": organization_id}
        ).sort("created_at", -1).to_list(100)
        
        return [PaymentTransaction(**payment) for payment in payments]

    def get_plan_config(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Get configuration for a subscription plan"""
        return PAYMENT_PLANS.get(plan, {})

    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available subscription plans"""
        return PAYMENT_PLANS

# Additional imports
from datetime import datetime
from typing import List