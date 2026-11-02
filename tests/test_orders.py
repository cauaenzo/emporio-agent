
import pytest

from app.tools.orders import OrderService


@pytest.fixture
def service():
    return OrderService()


def test_order_service_loads_data(service):
    assert len(service.orders) == 20
    assert len(service.order_items) == 22


def test_invalid_order_id_returns_none(service):
    result = service.get_order(-1, 1)

    assert result is None


def test_invalid_customer_id_returns_none(service):
    result = service.get_order(1, -1)

    assert result is None


def test_customer_without_orders_returns_empty_list(service):
    result = service.get_customer_orders(-1)

    assert result == []


def test_order_belongs_to_authenticated_customer(service):
    order = service.orders.iloc[0]

    order_id = int(order["order_id"])
    customer_id = int(order["customer_id"])

    result = service.get_order(order_id, customer_id)

    assert result is not None
    assert result["order_id"] == order_id


def test_customer_cannot_access_another_customers_order(service):
    order = service.orders.iloc[0]

    order_id = int(order["order_id"])
    owner_id = int(order["customer_id"])

    other_customer_id = (
        owner_id + 1 if owner_id != 999999 else owner_id - 1
    )

    result = service.get_order(
        order_id,
        other_customer_id,
    )

    assert result is None


def test_order_contains_items(service):
    order = service.orders.iloc[0]

    result = service.get_order(
        int(order["order_id"]),
        int(order["customer_id"]),
    )

    assert result is not None
    assert isinstance(result["items"], list)


def test_customer_orders_only_contain_basic_information(service):
    order = service.orders.iloc[0]
    customer_id = int(order["customer_id"])

    results = service.get_customer_orders(customer_id)

    assert all(
        set(item.keys()) == {
            "order_id",
            "order_date",
            "status",
            "total_brl",
        }
        for item in results
    )
