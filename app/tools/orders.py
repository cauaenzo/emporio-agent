
import pandas as pd

from app.config import DATA_FILES


class OrderService:
    """Responsável pelas consultas de pedidos."""

    def __init__(self):
        self.orders = pd.read_csv(DATA_FILES["orders"])
        self.order_items = pd.read_csv(DATA_FILES["order_items"])
        self.products = pd.read_csv(DATA_FILES["products"])

        self._validate_data()

    def _validate_data(self):
        required_orders = {
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "total_brl",
            "payment_method",
            "tracking_code",
            "estimated_delivery",
        }

        required_items = {
            "order_id",
            "quantity",
            "product_id",
        }

        missing_orders = required_orders - set(self.orders.columns)
        missing_items = required_items - set(self.order_items.columns)

        if missing_orders:
            raise ValueError(
                f"Colunas ausentes em orders: {missing_orders}"
            )

        if missing_items:
            raise ValueError(
                f"Colunas ausentes em order_items: {missing_items}"
            )

    def get_order(
        self,
        order_id: int,
        authenticated_customer_id: int,
    ) -> dict | None:
        """
        Consulta um pedido pertencente ao cliente autenticado.

        authenticated_customer_id deve vir de um contexto
        de autenticação confiável, nunca de uma informação
        arbitrária fornecida pelo modelo.
        """

        if order_id <= 0 or authenticated_customer_id <= 0:
            return None

        matches = self.orders[
            (self.orders["order_id"] == order_id)
            &
            (self.orders["customer_id"] == authenticated_customer_id)
        ]

        if matches.empty:
            return None

        order = matches.iloc[0]

        items = self.order_items[
            self.order_items["order_id"] == order_id
        ]

        products_by_id = self.products.set_index("product_id")

        order_items = []

        for _, item in items.iterrows():
            product_id = int(item["product_id"])

            product_name = (
                products_by_id.loc[product_id, "name"]
                if product_id in products_by_id.index
                else "Produto não identificado"
            )

            order_items.append({
                "product_id": product_id,
                "product_name": product_name,
                "quantity": int(item["quantity"]),
            })

        return {
            "order_id": int(order["order_id"]),
            "order_date": str(order["order_date"]),
            "status": str(order["status"]),
            "total_brl": float(order["total_brl"]),
            "payment_method": str(order["payment_method"]),
            "tracking_code": str(order["tracking_code"]),
            "estimated_delivery": str(order["estimated_delivery"]),
            "items": order_items,
        }

    def get_customer_orders(
        self,
        authenticated_customer_id: int,
    ) -> list[dict]:
        """Lista os pedidos do cliente autenticado."""

        if authenticated_customer_id <= 0:
            return []

        customer_orders = self.orders[
            self.orders["customer_id"] == authenticated_customer_id
        ]

        return [
            {
                "order_id": int(order["order_id"]),
                "order_date": str(order["order_date"]),
                "status": str(order["status"]),
                "total_brl": float(order["total_brl"]),
            }
            for _, order in customer_orders.iterrows()
        ]
