
from decimal import Decimal

import pytest

from app.services.store_rules import StoreRules


def test_pix_discount():
    result = StoreRules.calculate_pix_price(100)

    assert result == Decimal("95.00")


def test_free_shipping_above_minimum():
    result = StoreRules.calculate_shipping(500.01)

    assert result == Decimal("0.00")


def test_shipping_is_paid_at_minimum():
    result = StoreRules.calculate_shipping(500.00)

    assert result == Decimal("35.00")


def test_paid_shipping_below_minimum():
    result = StoreRules.calculate_shipping(400)

    assert result == Decimal("35.00")


def test_installment_calculation():
    result = StoreRules.calculate_installment(1200, 12)

    assert result == Decimal("100.00")


def test_invalid_installment_quantity():
    with pytest.raises(ValueError):
        StoreRules.calculate_installment(1200, 0)


def test_negative_price():
    with pytest.raises(ValueError):
        StoreRules.calculate_pix_price(-100)

    with pytest.raises(ValueError):
        StoreRules.calculate_shipping(-100)

    with pytest.raises(ValueError):
        StoreRules.calculate_installment(-100, 2)
