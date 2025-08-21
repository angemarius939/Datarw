"""
Mock IremboPay Payment Service Implementation
This service provides a complete mock implementation of IremboPay integration
that can be easily updated with real API credentials when available.
"""

import json
import uuid
import hmac
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PaymentProvider(str, Enum):
    MTN = "MTN"
    AIRTEL = "AIRTEL"
    CARD = "CARD"
    BANK = "BANK"

class MockIremboPayService:
    """
    Mock implementation of IremboPay service for development and testing.
    This implementation simulates all IremboPay API behaviors with realistic responses.
    """
    
    def __init__(self):
        self.mock_invoices = {}  # Store mock invoices
        self.mock_payments = {}  # Store mock payments
        self.webhook_secret = "mock_webhook_secret_key_for_development"
        self.api_key = "mock_api_key_for_development"
        
        # Pricing tiers configuration
        self.pricing_tiers = {
            "Basic": {"price": 100000, "currency": "RWF", "features": ["10 Surveys", "100 Responses", "Basic Analytics"]},
            "Professional": {"price": 300000, "currency": "RWF", "features": ["Unlimited Surveys", "10K Responses", "Advanced Analytics", "API Access"]},
            "Enterprise": {"price": "Custom", "currency": "RWF", "features": ["Unlimited Everything", "Priority Support", "Custom Integrations"]}
        }
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payment invoice (mock implementation)
        """
        try:
            # Generate mock invoice number
            invoice_number = f"880{random.randint(100000000, 999999999)}"
            transaction_id = invoice_data.get("transaction_id", str(uuid.uuid4()))
            
            # Calculate total amount
            total_amount = sum(
                item.get("unit_amount", 0) * item.get("quantity", 1)
                for item in invoice_data.get("payment_items", [])
            )
            
            # Mock invoice response
            mock_invoice = {
                "invoiceNumber": invoice_number,
                "transactionId": transaction_id,
                "status": PaymentStatus.PENDING,
                "amount": total_amount,
                "currency": invoice_data.get("currency", "RWF"),
                "paymentUrl": f"https://mock.irembopay.com/pay/{invoice_number}",
                "customer": invoice_data.get("customer", {}),
                "description": invoice_data.get("description", ""),
                "expiryAt": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "createdAt": datetime.utcnow().isoformat(),
                "paymentMethods": ["MTN", "AIRTEL", "CARD", "BANK"]
            }
            
            # Store mock invoice
            self.mock_invoices[invoice_number] = mock_invoice
            
            logger.info(f"Mock invoice created: {invoice_number} for amount {total_amount} RWF")
            
            # Simulate processing delay
            await asyncio.sleep(0.1)
            
            return mock_invoice
            
        except Exception as e:
            logger.error(f"Error creating mock invoice: {str(e)}")
            raise Exception(f"Failed to create invoice: {str(e)}")
    
    async def initiate_mobile_money_payment(
        self, 
        invoice_number: str, 
        phone_number: str, 
        provider: PaymentProvider
    ) -> Dict[str, Any]:
        """
        Initiate mobile money payment (mock implementation)
        """
        try:
            invoice = self.mock_invoices.get(invoice_number)
            if not invoice:
                raise Exception(f"Invoice {invoice_number} not found")
            
            # Generate payment reference
            payment_reference = f"{provider}-{random.randint(100000, 999999)}"
            
            # Mock payment initiation response
            payment_response = {
                "paymentReference": payment_reference,
                "status": PaymentStatus.PROCESSING,
                "message": f"Payment request sent to {phone_number}. Please check your {provider} mobile money and confirm payment.",
                "amount": invoice["amount"],
                "currency": invoice["currency"],
                "provider": provider,
                "phoneNumber": phone_number,
                "estimatedProcessingTime": "2-5 minutes"
            }
            
            # Store payment
            self.mock_payments[payment_reference] = {
                **payment_response,
                "invoiceNumber": invoice_number,
                "transactionId": invoice.get("transactionId"),
                "initiatedAt": datetime.utcnow().isoformat()
            }
            
            # Update invoice status
            invoice["status"] = PaymentStatus.PROCESSING
            
            logger.info(f"Mock mobile money payment initiated: {payment_reference}")
            
            # Simulate async payment processing (will complete after 30 seconds for demo)
            asyncio.create_task(self._simulate_payment_completion(payment_reference, invoice_number))
            
            await asyncio.sleep(0.1)
            return payment_response
            
        except Exception as e:
            logger.error(f"Error initiating mock mobile money payment: {str(e)}")
            raise Exception(f"Failed to initiate payment: {str(e)}")
    
    async def _simulate_payment_completion(self, payment_reference: str, invoice_number: str):
        """
        Simulate payment completion after delay (for demo purposes)
        """
        try:
            # Wait 30 seconds to simulate real payment processing
            await asyncio.sleep(30)
            
            # 90% success rate simulation
            success = random.random() < 0.9
            
            payment = self.mock_payments.get(payment_reference)
            invoice = self.mock_invoices.get(invoice_number)
            
            if payment and invoice:
                if success:
                    # Mark payment as completed
                    payment["status"] = PaymentStatus.COMPLETED
                    payment["completedAt"] = datetime.utcnow().isoformat()
                    payment["paymentId"] = f"PAY-{random.randint(1000000, 9999999)}"
                    
                    invoice["status"] = PaymentStatus.COMPLETED
                    invoice["completedAt"] = datetime.utcnow().isoformat()
                    
                    logger.info(f"Mock payment completed successfully: {payment_reference}")
                    
                    # Trigger webhook notification
                    await self._send_mock_webhook("payment.completed", {
                        "invoiceNumber": invoice_number,
                        "transactionId": invoice.get("transactionId"),
                        "paymentReference": payment_reference,
                        "amount": payment["amount"],
                        "currency": payment["currency"],
                        "provider": payment["provider"],
                        "completedAt": payment["completedAt"]
                    })
                else:
                    # Mark payment as failed
                    payment["status"] = PaymentStatus.FAILED
                    payment["failedAt"] = datetime.utcnow().isoformat()
                    payment["failureReason"] = "Insufficient funds or payment cancelled by user"
                    
                    invoice["status"] = PaymentStatus.FAILED
                    
                    logger.info(f"Mock payment failed: {payment_reference}")
                    
                    # Trigger failure webhook
                    await self._send_mock_webhook("payment.failed", {
                        "invoiceNumber": invoice_number,
                        "transactionId": invoice.get("transactionId"),
                        "paymentReference": payment_reference,
                        "failureReason": payment["failureReason"],
                        "failedAt": payment["failedAt"]
                    })
                    
        except Exception as e:
            logger.error(f"Error in mock payment completion: {str(e)}")
    
    async def get_invoice_status(self, invoice_number: str) -> Dict[str, Any]:
        """
        Get invoice status (mock implementation)
        """
        try:
            invoice = self.mock_invoices.get(invoice_number)
            if not invoice:
                raise Exception(f"Invoice {invoice_number} not found")
            
            await asyncio.sleep(0.1)  # Simulate API delay
            
            return {
                "invoiceNumber": invoice_number,
                "status": invoice["status"],
                "amount": invoice["amount"],
                "currency": invoice["currency"],
                "transactionId": invoice.get("transactionId"),
                "createdAt": invoice["createdAt"],
                "expiryAt": invoice["expiryAt"],
                "completedAt": invoice.get("completedAt"),
                "paymentMethod": invoice.get("paymentMethod"),
                "lastUpdated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting mock invoice status: {str(e)}")
            raise Exception(f"Failed to get invoice status: {str(e)}")
    
    async def get_payment_status(self, payment_reference: str) -> Dict[str, Any]:
        """
        Get payment status (mock implementation)
        """
        try:
            payment = self.mock_payments.get(payment_reference)
            if not payment:
                raise Exception(f"Payment {payment_reference} not found")
            
            await asyncio.sleep(0.1)  # Simulate API delay
            
            return {
                "paymentReference": payment_reference,
                "status": payment["status"],
                "amount": payment["amount"], 
                "currency": payment["currency"],
                "provider": payment["provider"],
                "phoneNumber": payment["phoneNumber"],
                "initiatedAt": payment["initiatedAt"],
                "completedAt": payment.get("completedAt"),
                "failedAt": payment.get("failedAt"),
                "failureReason": payment.get("failureReason")
            }
            
        except Exception as e:
            logger.error(f"Error getting mock payment status: {str(e)}")
            raise Exception(f"Failed to get payment status: {str(e)}")
    
    def generate_webhook_signature(self, payload: str) -> str:
        """
        Generate webhook signature for mock webhooks
        """
        return hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature
        """
        expected_signature = self.generate_webhook_signature(payload)
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def _send_mock_webhook(self, event_type: str, event_data: Dict[str, Any]):
        """
        Simulate sending webhook notification to our application
        """
        try:
            import httpx
            
            webhook_payload = {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "createdAt": datetime.utcnow().isoformat(),
                "data": event_data
            }
            
            payload_str = json.dumps(webhook_payload)
            signature = f"sha256={self.generate_webhook_signature(payload_str)}"
            
            # In a real implementation, this would be sent to your webhook endpoint
            # For now, we'll just log it
            logger.info(f"Mock webhook would be sent: {event_type} with signature {signature}")
            
            # Optionally, make actual HTTP request to webhook endpoint for testing
            # async with httpx.AsyncClient() as client:
            #     await client.post(
            #         "http://localhost:8001/api/webhooks/irembopay",
            #         json=webhook_payload,
            #         headers={"X-IremboPay-Signature": signature}
            #     )
            
        except Exception as e:
            logger.error(f"Error sending mock webhook: {str(e)}")
    
    def get_pricing_tiers(self) -> Dict[str, Any]:
        """
        Get available pricing tiers
        """
        return self.pricing_tiers
    
    async def create_subscription_payment(
        self, 
        user_email: str,
        user_name: str,
        phone_number: str,
        plan_name: str,
        payment_method: str = "MTN"
    ) -> Dict[str, Any]:
        """
        Create subscription payment for DataRW plans
        """
        try:
            if plan_name not in self.pricing_tiers:
                raise Exception(f"Invalid plan: {plan_name}")
            
            plan = self.pricing_tiers[plan_name]
            if plan["price"] == "Custom":
                raise Exception("Enterprise plan requires custom pricing. Please contact sales.")
            
            # Create invoice for subscription
            invoice_data = {
                "transaction_id": f"SUB-{plan_name.upper()}-{uuid.uuid4().hex[:12]}",
                "customer": {
                    "email": user_email,
                    "name": user_name,
                    "phone_number": phone_number
                },
                "payment_items": [{
                    "unit_amount": plan["price"],
                    "quantity": 1,
                    "code": f"PLAN-{plan_name.upper()}",
                    "description": f"DataRW {plan_name} Plan - Monthly Subscription"
                }],
                "description": f"DataRW {plan_name} Plan Subscription",
                "currency": "RWF"
            }
            
            invoice = await self.create_invoice(invoice_data)
            
            # If mobile money, initiate payment immediately
            if payment_method in ["MTN", "AIRTEL"]:
                payment_response = await self.initiate_mobile_money_payment(
                    invoice["invoiceNumber"],
                    phone_number,
                    PaymentProvider(payment_method)
                )
                
                return {
                    "invoice": invoice,
                    "payment": payment_response,
                    "plan": plan_name,
                    "amount": plan["price"],
                    "currency": "RWF"
                }
            else:
                return {
                    "invoice": invoice,
                    "payment_url": invoice["paymentUrl"],
                    "plan": plan_name,
                    "amount": plan["price"],
                    "currency": "RWF"
                }
                
        except Exception as e:
            logger.error(f"Error creating subscription payment: {str(e)}")
            raise Exception(f"Failed to create subscription payment: {str(e)}")

# Global instance
irembopay_service = MockIremboPayService()