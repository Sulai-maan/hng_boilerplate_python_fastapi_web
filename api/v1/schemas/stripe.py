from typing import List, Optional
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date 


class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=16, max_length=16)
    exp_month: int
    exp_year: int
    cvc: str = Field(..., min_length=3, max_length=4)

    @field_validator('card_number')
    @classmethod
    def card_number_validator(cls, v):
        if not v.isdigit() or len(v) != 16:
            raise ValueError('Card number must be 16 digits')
        return v

    @field_validator('cvc')
    @classmethod
    def cvc_validator(cls, v):
        if not v.isdigit() or not (3 <= len(v) <= 4):
            raise ValueError('CVC must be 3 or 4 digits')
        return v

    @model_validator()
    def card_expiry_validator(self: Self) -> Self:
        today = date.today()
        expiry_date = date(self.exp_year, self.exp_month, 1)

        if today.replace(day=1) > expiry_date:
            raise ValueError('Card has expired')
        return self



class PlanUpgradeRequest(BaseModel):
    user_id: str
    plan_id: str
    is_downgrade: bool
    #payment_info: Optional[PaymentInfo] = None


