
import pandas as pd
import pytest

from app.tools.products import ProductCatalog


@pytest.fixture
def catalog():
    return ProductCatalog()


@pytest.fixture
def availability_catalog(catalog):
    catalog.products = pd.DataFrame([
        {
            "product_id": 1,
            "name": "Yamaha descontinuado",
            "description": "Violão de nylon",
            "price_brl": 500.00,
            "category_id": 1,
            "stock_quantity": 10,
            "status": "discontinued",
            "specs": "",
        },
        {
            "product_id": 2,
            "name": "Yamaha sem estoque",
            "description": "Violão de nylon",
            "price_brl": 600.00,
            "category_id": 1,
            "stock_quantity": 0,
            "status": "active",
            "specs": "",
        },
        {
            "product_id": 3,
            "name": "Yamaha disponível",
            "description": "Violão de nylon",
            "price_brl": 700.00,
            "category_id": 1,
            "stock_quantity": 5,
            "status": "active",
            "specs": "",
        },
        {
            "product_id": 4,
            "name": "Yamaha disponível 2",
            "description": "Violão de nylon",
            "price_brl": 800.00,
            "category_id": 1,
            "stock_quantity": 3,
            "status": "active",
            "specs": "",
        },
    ])

    return catalog


def test_catalog_loads_products(catalog):
    assert len(catalog.products) == 65


def test_search_products_by_name(catalog):
    results = catalog.search_products("Yamaha")

    assert len(results) > 0
    assert any(
        "Yamaha" in product["name"]
        for product in results
    )


def test_search_products_by_description(catalog):
    results = catalog.search_products("Spruce")

    assert len(results) > 0


def test_search_products_without_results(catalog):
    results = catalog.search_products("ProdutoInexistente123")

    assert results == []


def test_search_products_with_empty_query(catalog):
    results = catalog.search_products("   ")

    assert results == []


def test_get_product_by_id(catalog):
    product = catalog.get_product_by_id(81)

    assert product is not None
    assert product["name"] == "Yamaha C40 Nylon Natural"


def test_get_product_with_invalid_id(catalog):
    product = catalog.get_product_by_id(-1)

    assert product is None


def test_get_product_price(catalog):
    price = catalog.get_product_price(81)

    assert price == pytest.approx(599.90)


def test_get_price_for_nonexistent_product(catalog):
    price = catalog.get_product_price(-1)

    assert price is None


def test_available_products(catalog):
    products = catalog.get_available_products()

    assert all(
        product["status"] == "active"
        and product["stock_quantity"] > 0
        for product in products
    )


def test_search_available_products_filters_before_limit(
    availability_catalog,
):
    results = availability_catalog.search_products(
        "Yamaha",
        limit=1,
        available_only=True,
    )

    assert len(results) == 1
    assert results[0]["product_id"] == 3


def test_search_without_availability_filter_includes_all(
    availability_catalog,
):
    results = availability_catalog.search_products(
        "Yamaha",
        limit=4,
    )

    assert len(results) == 4


def test_active_product_without_stock_is_not_available(
    availability_catalog,
):
    results = availability_catalog.search_products(
        "Yamaha",
        limit=4,
        available_only=True,
    )

    product_ids = [product["product_id"] for product in results]

    assert 2 not in product_ids


def test_discontinued_product_with_stock_is_not_available(
    availability_catalog,
):
    results = availability_catalog.search_products(
        "Yamaha",
        limit=4,
        available_only=True,
    )

    product_ids = [product["product_id"] for product in results]

    assert 1 not in product_ids


def test_search_available_products_respects_limit(
    availability_catalog,
):
    results = availability_catalog.search_products(
        "Yamaha",
        limit=1,
        available_only=True,
    )

    assert len(results) == 1
    assert results[0]["status"] == "active"
    assert results[0]["stock_quantity"] > 0
