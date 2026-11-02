import pytest

from app.tools.promotions import PromotionService


@pytest.fixture
def service():
    return PromotionService()


def test_load_promotions(service):
    assert len(service.promotions) == 25


def test_get_active_promotions(service):
    promotions = service.get_active_promotions()

    assert len(promotions) == 4
    assert all(p["is_active"] == 1 for p in promotions)


def test_invalid_product_id(service):
    assert service.get_product_promotion(-1) is None


def test_product_without_promotion(service):
    assert service.get_product_promotion(81) is None


def test_discount_calculation_without_promotion(service):
    assert service.calculate_discounted_price(599.90, 81) is None