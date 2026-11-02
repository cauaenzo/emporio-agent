
from app.tools.products import ProductCatalog
from app.tools.promotions import PromotionService
from app.services.store_rules import StoreRules
from app.services.policy_service import PolicyService


class StoreService:
    """Centraliza as operações disponíveis para o agente da loja."""

    def __init__(self):
        self.products = ProductCatalog()
        self.promotions = PromotionService()
        self._policy_service = None

    @property
    def policy_service(self):
        """Carrega o serviço RAG somente quando necessário."""

        if self._policy_service is None:
            self._policy_service = PolicyService()

        return self._policy_service

    def search_products(
        self,
        query: str,
        limit: int = 5,
        available_only: bool = False,
    ) -> list[dict]:

        return self.products.search_products(
            query=query,
            limit=limit,
            available_only=available_only,
        )

    def get_product(self, product_id: int) -> dict | None:
        return self.products.get_product_by_id(product_id)

    def get_product_price_options(
        self,
        product_id: int,
    ) -> dict | None:

        product = self.products.get_product_by_id(product_id)

        if product is None:
            return None

        base_price = float(product["price_brl"])

        promotion = self.promotions.get_product_promotion(
            product_id
        )

        if promotion is not None:
            promotional_price = (
                self.promotions.calculate_discounted_price(
                    price=base_price,
                    product_id=product_id,
                )
            )

            return {
                "product_id": product_id,
                "base_price": base_price,
                "promotion": {
                    "description": promotion["description"],
                    "discount_percent": float(
                        promotion["discount_percent"]
                    ),
                    "promotional_price": promotional_price,
                },
                "pix_price": None,
                "pix_discount_applied": False,
            }

        pix_price = StoreRules.calculate_pix_price(base_price)

        return {
            "product_id": product_id,
            "base_price": base_price,
            "promotion": None,
            "pix_price": float(pix_price),
            "pix_discount_applied": True,
        }

    def search_policy(
        self,
        question: str,
        top_k: int = 3,
    ) -> dict:
        """Consulta as informações do manual da loja."""

        return self.policy_service.search_policy(
            question=question,
            top_k=top_k,
        )
