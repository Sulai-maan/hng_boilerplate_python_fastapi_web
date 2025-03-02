import stripe, json

from fastapi import Depends, APIRouter, status, Query, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.utils.success_response import success_response, fail_response
from api.utils.db_validators import check_model_existence
from api.v1.schemas.payment import PaymentDetail
from api.v1.services.payment import PaymentService
from api.v1.services.user import user_service
from api.db.database import get_db
from api.v1.models import User
from api.v1.routes.payment import payment
from api.v1.models.billing_plan import BillingPlan
from api.utils.settings import settings

@payment.post("/pay_with_stripe", response_model=success_response)
async def create_payment_intent(
    request: PaymentDetail,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)  
    ):
    """
    Stripe payment integration - initialize payment
    """
    try:
        plan = check_model_existence(db, BillingPlan, request.plan_id)
        amount = plan.price
        currency = plan.currency
        stripe.api_key=settings.STRIPE_SECRET
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=current_user.id
        )

        #save payment details
        payment_service = PaymentService()
        payment_data = {
            "user_id": current_user.id,
            "amount": float(plan.price),
            "currency": plan.currency,
            "status": "initiated",
            "method": "Auto",
            "transaction_id": intent["id"]
        }

        payment_service.create(db, payment_data)
        data = {'client_secret':intent["client_secret"]}
        return success_response(status_code=status.HTTP_200_OK, message="payment initiated", data=data) 
    except HTTPException():
        return fail_response(status_code=status.HTTP_400_BAD_REQUEST, message="Plan doesn't exist")
    except stripe.error.StripeError as e:
        print(e)
        return fail_response(status_code=status.HTTP_400_BAD_REQUEST, message="Error initializing payment")


@payment.post("/stripe/webhook", response_model=success_response)
async def payment_status(request: Request, db: Session = Depends(get_db)):
    
    try:
        payload = await request.body
        payload = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        return fail_response(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Webhook error while parsing basic request: str({e})")
    
    # Check to confirm that request is from Stripe
    stripe_sign = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_sign, settings.STRIPE_WEBHOOK_SECRET
        )
        # return success_response(status_code=status.HTTP_200_OK, message="Webhook received")
    except ValueError:
        return fail_response(status_code=status.HTTP_400_BAD_REQUEST, message="Invalid payload")
    except stripe.error.SignatureVerificationError:
        return fail_response(status_code=status.HTTP_400_BAD_REQUEST, message="Invalid signature")

    # Handle successful payments
    # if event["type"] == "payment_intent.succeeded":
    #     payment_intent = event["data"]["object"]
    #     payment_service = PaymentService()

    #     payment_service.update(db, payment_intent['id'], )

    #     print(f"Payment {} succeeded!")

    # return {"message": "Webhook received"}


