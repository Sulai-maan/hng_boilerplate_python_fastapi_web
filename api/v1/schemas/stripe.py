from typing import List, Optional
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date 


class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=16, max_length=16)
    exp_month: int = Field(...,ge=1, le=12)
    exp_year: int = Field(..., ge=date.today().year)
    cvc: str = Field(..., min_length=3, max_length=4)

    @field_validator('card_number')
    @classmethod
    def card_number_validator(cls, v):
        # Length already enforced above with Field(min_length, max_length)
        if not v.isdigit():
            raise ValueError('Card number must be 16 digits')
        return v

    @field_validator('cvc')
    @classmethod
    def cvc_validator(cls, v):
        # Length already enforced above with Field(min_length, max_length)
        if not v.isdigit():
            raise ValueError('CVC must be 3 or 4 digits')
        return v

    @model_validator(mode="after")
    def card_expiry_validator(self: Self) -> Self:
        today = date.today()
        if (self.exp_year == today.year) and (self.exp_month < today.month): 
            raise ValueError('Card has expired')
        return self



class PlanUpgradeRequest(BaseModel):
    user_id: str
    plan_id: str
    is_downgrade: bool
    #payment_info: Optional[PaymentInfo] = None


