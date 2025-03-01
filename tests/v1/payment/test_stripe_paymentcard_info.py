from api.v1.schemas.stripe import PaymentInfo
import pytest
from pydantic import BaseModel, ValidationError
from datetime import time, date


def test_incomplete_card_number():

    with pytest.raises(ValueError) as excinfo:
        card = PaymentInfo(
            card_number = "41424344454648",
            exp_month = 12,
            exp_year = 2022,
            cvc = "432"
        )
    
    assert "at least 16 characters" in str(excinfo.value)

    
def test_incorrect_cvc_input():
    
    with pytest.raises(ValueError) as excinfo:
        card = PaymentInfo(
            card_number = "4142434445464748",
            exp_month = 12,
            exp_year = 2022,
            cvc = "43256"
        )

    assert "string_too_long" in str(excinfo.value)

def test_expired_card_info():
    with pytest.raises(ValueError) as excinfo:
        card = PaymentInfo(
            card_number = "4142434445464748",
            exp_month = 12,
            exp_year = date.today().year - 1,
            cvc = "4325"
    )

    assert "greater than or equal to 2025" in str(excinfo.value)

def test_invalid_card_expiry_date():
    with pytest.raises(ValueError) as excinfo:
        card = PaymentInfo(
            card_number = "4142434445464748",
            exp_month = 14,
            exp_year = date.today().year + 1,
            cvc = "4325"
    )

    assert "less than or equal to 12" in str(excinfo.value)        

def test_valid_card_creation():

    next_year = date.today().year + 1
    card = PaymentInfo(
        card_number = "4111111111111111",
        exp_month = 12,
        exp_year = next_year,
        cvc = "123"
    )
    
    assert card.card_number == "4111111111111111"
    assert card.exp_month == 12
    assert card.exp_year == next_year
    assert card.cvc == "123"


