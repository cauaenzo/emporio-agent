import pandas as pd

from app.config import DATA_FILES


class PromotionService:
    """Responsável pelas consultas e cálculos de promoções."""

    def __init__(self):
        self.promotions = pd.read_csv(DATA_FILES["promotions"])
        self._validate_data()

    def _validate_data(self):
        required_columns = {
            "promotion_id",
            "product_id",
            "discount_percent",
            "description",
            "is_active",
        }

        missing_columns = required_columns - set(self.promotions.columns)

        if missing_columns:
            raise ValueError(
                f"Colunas ausentes em promotions: {missing_columns}"
            )

        if self.promotions["promotion_id"].duplicated().any():
            raise ValueError("Existem IDs de promoções duplicados.")

        if not self.promotions["discount_percent"].between(0, 100).all():
            raise ValueError("Existem percentuais de desconto inválidos.")

    def get_active_promotions(self) -> list[dict]:
        """Retorna todas as promoções ativas."""

        active = self.promotions[
            self.promotions["is_active"] == 1
        ]

        return active.to_dict(orient="records")

    def get_product_promotion(self, product_id: int) -> dict | None:
        """Busca uma promoção ativa associada a um produto."""

        if product_id <= 0:
            return None

        matches = self.promotions[
            (self.promotions["product_id"] == product_id)
            & (self.promotions["is_active"] == 1)
        ]

        if matches.empty:
            return None

        return matches.iloc[0].to_dict()

    def calculate_discounted_price(
        self,
        price: float,
        product_id: int,
    ) -> float | None:
        """Calcula o preço com a promoção ativa do produto."""

        if price < 0:
            raise ValueError("O preço não pode ser negativo.")

        promotion = self.get_product_promotion(product_id)

        if promotion is None:
            return None

        discount = promotion["discount_percent"] / 100

        return round(price * (1 - discount), 2)