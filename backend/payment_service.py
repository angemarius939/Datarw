import aiohttp
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from models import PaymentTransaction, PaymentTransactionCreate, SubscriptionPlan, PaymentStatus, IremboPayInvoiceRequest, IremboPayInvoiceResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

# IremboPay Configuration
IREMBOPAY_SECRET_KEY = os.environ.get("IREMBOPAY_SECRET_KEY", "")
IREMBOPAY_PUBLIC_KEY = os.environ.get("IREMBOPAY_PUBLIC_KEY", "")
IREMBOPAY_PAYMENT_ACCOUNT_ID = os.environ.get("IREMBOPAY_PAYMENT_ACCOUNT_ID", "")
IREMBOPAY_IS_PRODUCTION = os.environ.get("IREMBOPAY_PRODUCTION", "false").lower() == "true"

# API URLs
if IREMBOPAY_IS_PRODUCTION:
    IREMBOPAY_API_BASE = "https://api.irembopay.com"
    IREMBOPAY_WIDGET_URL = "https://dashboard.irembopay.com/assets/payment/inline.js"
else:
    IREMBOPAY_API_BASE = "https://api.sandbox.irembopay.com"
    IREMBOPAY_WIDGET_URL = "https://dashboard.sandbox.irembopay.com/assets/payment/inline.js"

# Payment Plans Configuration
PAYMENT_PLANS = {
    SubscriptionPlan.BASIC: {
        "amount": 100000.0,  # 100,000 FRW
        "currency": "RWF",
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
        "currency": "RWF", 
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
        "currency": "RWF",
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

class IremboPayService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.headers = {
            "Content-Type": "application/json",
            "irembopay-secretkey": IREMBOPAY_SECRET_KEY,
            "X-API-Version": "2"
        }
        
        if not IREMBOPAY_SECRET_KEY:
            logger.warning("IremboPay secret key not configured")

    async def create_invoice(
        self,
        organization_id: str,
        plan: SubscriptionPlan,
        user_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None
    ) -> IremboPayInvoiceResponse:
        """Create an IremboPay invoice for a subscription plan"""
        
        if not IREMBOPAY_SECRET_KEY:
            raise ValueError("IremboPay not configured")
        
        # Get plan configuration
        plan_config = PAYMENT_PLANS.get(plan)
        if not plan_config:
            raise ValueError(f"Invalid plan: {plan}")
        
        if plan == SubscriptionPlan.ENTERPRISE:
            raise ValueError("Enterprise plans require custom pricing")
        
        # Generate unique transaction ID
        transaction_id = f"DATARW_{organization_id}_{plan.value}_{int(datetime.utcnow().timestamp())}"
        
        # Prepare invoice request
        invoice_request = {
            "transactionId": transaction_id,
            "paymentAccountIdentifier": IREMBOPAY_PAYMENT_ACCOUNT_ID,
            "paymentItems": [
                {
                    "code": f"DATARW_{plan.value}",
                    "quantity": 1,
                    "unitAmount": plan_config["amount"]
                }
            ],
            "description": f"DataRW {plan.value} Plan Subscription",
            "language": "EN"
        }
        
        # Add customer information if provided
        if customer_name or customer_email or customer_phone:
            invoice_request["customer"] = {}
            if customer_name:
                invoice_request["customer"]["name"] = customer_name
            if customer_email:
                invoice_request["customer"]["email"] = customer_email
            if customer_phone:
                invoice_request["customer"]["phoneNumber"] = customer_phone
        
        # Set expiry to 24 hours from now
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        invoice_request["expiryAt"] = expiry_time.strftime("%Y-%m-%dT%H:%M:%S.000+02:00")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{IREMBOPAY_API_BASE}/payments/invoices",
                    json=invoice_request,
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 201 and response_data.get("success"):
                        data = response_data["data"]
                        
                        # Store payment transaction in database
                        payment_transaction = PaymentTransactionCreate(
                            organization_id=organization_id,
                            user_id=user_id,
                            irembopay_invoice_number=data["invoiceNumber"],
                            transaction_id=transaction_id,
                            amount=plan_config["amount"],
                            currency=plan_config["currency"],
                            plan=plan,
                            metadata={
                                "customer_name": customer_name,
                                "customer_email": customer_email,
                                "customer_phone": customer_phone
                            }
                        )
                        
                        payment_doc = PaymentTransaction(**payment_transaction.dict())
                        await self.db.payment_transactions.insert_one(payment_doc.dict(by_alias=True))
                        
                        logger.info(f"Created IremboPay invoice {data['invoiceNumber']} for organization {organization_id}")
                        
                        return IremboPayInvoiceResponse(
                            success=True,
                            invoice_number=data["invoiceNumber"],
                            payment_link_url=data["paymentLinkUrl"],
                            amount=data["amount"],
                            currency=data["currency"],
                            status=data["paymentStatus"]
                        )
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"IremboPay invoice creation failed: {error_msg}")
                        raise ValueError(f"Invoice creation failed: {error_msg}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"IremboPay API request failed: {str(e)}")
            raise ValueError(f"Payment service unavailable: {str(e)}")

    async def get_invoice_status(self, invoice_number: str) -> Dict[str, Any]:
        """Get the status of an IremboPay invoice"""
        
        if not IREMBOPAY_SECRET_KEY:
            raise ValueError("IremboPay not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{IREMBOPAY_API_BASE}/payments/invoices/{invoice_number}",
                    headers=self.headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get("success"):
                        data = response_data["data"]
                        
                        # Update payment transaction in database
                        payment_transaction = await self.db.payment_transactions.find_one(
                            {"irembopay_invoice_number": invoice_number}
                        )
                        
                        if payment_transaction:
                            update_data = {
                                "payment_status": self._map_irembopay_status(data["paymentStatus"]),
                                "updated_at": datetime.utcnow()
                            }
                            
                            if data["paymentStatus"] == "PAID":
                                update_data["payment_reference"] = data.get("paymentReference")
                                update_data["payment_method"] = data.get("paymentMethod")
                                update_data["irembopay_transaction_id"] = data.get("transactionId")
                            
                            # If payment successful and not already processed
                            if (data["paymentStatus"] == "PAID" and 
                                payment_transaction.get("payment_status") != PaymentStatus.PAID):
                                
                                # Update organization subscription
                                await self._update_organization_subscription(
                                    payment_transaction["organization_id"],
                                    payment_transaction["plan"]
                                )
                                
                                logger.info(f"Payment successful for invoice {invoice_number}")
                            
                            await self.db.payment_transactions.update_one(
                                {"irembopay_invoice_number": invoice_number},
                                {"$set": update_data}
                            )
                        
                        return data
                    else:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error(f"IremboPay invoice status check failed: {error_msg}")
                        raise ValueError(f"Status check failed: {error_msg}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"IremboPay API request failed: {str(e)}")
            raise ValueError(f"Payment service unavailable: {str(e)}")

    def _map_irembopay_status(self, irembopay_status: str) -> PaymentStatus:
        """Map IremboPay payment status to our PaymentStatus enum"""
        mapping = {
            "NEW": PaymentStatus.PENDING,
            "PAID": PaymentStatus.PAID,
            "EXPIRED": PaymentStatus.EXPIRED,
            "FAILED": PaymentStatus.FAILED
        }
        return mapping.get(irembopay_status, PaymentStatus.PENDING)

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

    def get_widget_config(self) -> Dict[str, str]:
        """Get IremboPay widget configuration"""
        return {
            "widget_url": IREMBOPAY_WIDGET_URL,
            "public_key": IREMBOPAY_PUBLIC_KEY,
            "is_production": str(IREMBOPAY_IS_PRODUCTION).lower()
        }

    async def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify IremboPay webhook signature"""
        try:
            # Parse signature header: t=timestamp,s=signature
            parts = signature.split(',')
            timestamp = None
            received_signature = None
            
            for part in parts:
                key, value = part.split('=', 1)
                if key == 't':
                    timestamp = value
                elif key == 's':
                    received_signature = value
            
            if not timestamp or not received_signature:
                return False
            
            # Create expected signature
            payload_to_hash = f"{timestamp}#{payload}"
            expected_signature = hmac.new(
                IREMBOPAY_SECRET_KEY.encode(),
                payload_to_hash.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, received_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

# Additional imports
from datetime import datetime
from typing import List