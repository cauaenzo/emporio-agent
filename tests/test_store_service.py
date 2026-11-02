
import pytest

from app.services.store_service import StoreService


@pytest.fixture(scope="module")
def store():
    return StoreService()


def test_store_service_loads_catalog(store):
    assert len(store.products.products) > 0


def test_search_products(store):
    results = store.search_products("Yamaha")

    assert isinstance(results, list)
    assert len(results) > 0

    for product in results:
        assert "name" in product
        assert "price_brl" in product


def test_get_product(store):
    product_id = int(
        store.products.products.iloc[0]["product_id"]
    )

    product = store.get_product(product_id)

    assert product is not None
    assert product["product_id"] == product_id


def test_get_nonexistent_product(store):
    assert store.get_product(-1) is None


def test_product_price_options(store):
    product_id = int(
        store.products.products.iloc[0]["product_id"]
    )

    result = store.get_product_price_options(product_id)

    assert result is not None
    assert result["base_price"] >= 0

    if result["promotion"] is not None:
        assert result["pix_price"] is None
        assert result["pix_discount_applied"] is False

        assert (
            result["promotion"]["promotional_price"]
            <= result["base_price"]
        )
    else:
        assert result["pix_price"] is not None
        assert result["pix_price"] < result["base_price"]
        assert result["pix_discount_applied"] is True


def test_policy_service_is_loaded_lazily(store):
    assert store._policy_service is None


def test_store_service_policy_search(store):
    result = store.search_policy(
        "Qual é o desconto para pagamento via PIX?"
    )

    assert result["found"] is True
    assert len(result["results"]) > 0
