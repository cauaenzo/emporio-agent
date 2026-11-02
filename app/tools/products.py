
import re
import unicodedata

import pandas as pd

from app.config import DATA_FILES


class ProductCatalog:
    STOPWORDS = {
        "violao",
        "violoes",
        "instrumento",
        "instrumentos",
        "musical",
        "musicais",
        "produto",
        "produtos",
        "disponivel",
        "disponiveis",
        "estoque",
        "marca",
        "modelo",
        "quero",
        "procuro",
        "tem",
        "ter",
        "com",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "um",
        "uma",
        "os",
        "as",
    }

    def __init__(self):
        self.products = pd.read_csv(DATA_FILES["products"])
        self._validate_data()

    def _validate_data(self):
        required_columns = {
            "product_id",
            "price_brl",
            "name",
            "category_id",
            "description",
            "stock_quantity",
            "status",
            "specs",
        }

        missing_columns = required_columns - set(self.products.columns)

        if missing_columns:
            raise ValueError(
                f"Colunas ausentes no catálogo: {missing_columns}"
            )

        if self.products["product_id"].duplicated().any():
            raise ValueError("Existem IDs de produtos duplicados.")

        self.products["stock_quantity"] = pd.to_numeric(
            self.products["stock_quantity"],
            errors="coerce",
        ).fillna(0).astype(int)

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = unicodedata.normalize("NFKD", str(value))

        value = "".join(
            char
            for char in value
            if not unicodedata.combining(char)
        )

        return value.casefold()

    @staticmethod
    def _is_available(product: dict) -> bool:
        return (
            str(product["status"]).casefold() == "active"
            and int(product["stock_quantity"]) > 0
        )

    def search_products(
        self,
        query: str,
        limit: int = 5,
        available_only: bool = False,
    ) -> list[dict]:

        if not query or not query.strip():
            return []

        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")

        tokens = re.findall(
            r"\w+",
            self._normalize_text(query),
        )

        tokens = [
            token
            for token in tokens
            if token not in self.STOPWORDS
        ]

        if not tokens:
            return []

        searchable = (
            self.products["name"].fillna("").astype(str)
            + " "
            + self.products["description"].fillna("").astype(str)
        ).map(self._normalize_text)

        relevant_tokens = [
            token
            for token in tokens
            if searchable.str.contains(
                re.escape(token),
                regex=True,
            ).any()
        ]

        if not relevant_tokens:
            return []

        matches_mask = pd.Series(
            True,
            index=self.products.index,
        )

        for token in relevant_tokens:
            matches_mask &= searchable.str.contains(
                re.escape(token),
                regex=True,
            )

        matches = self.products[matches_mask]

        if available_only:
            matches = matches[
                (matches["status"].str.casefold() == "active")
                & (matches["stock_quantity"] > 0)
            ]

        return matches.head(limit).to_dict(orient="records")

    def get_product_by_id(self, product_id: int) -> dict | None:
        matches = self.products[
            self.products["product_id"] == product_id
        ]

        if matches.empty:
            return None

        return matches.iloc[0].to_dict()

    def get_available_products(self) -> list[dict]:
        available = self.products[
            (self.products["status"].str.casefold() == "active")
            & (self.products["stock_quantity"] > 0)
        ]

        return available.to_dict(orient="records")

    def get_product_price(self, product_id: int) -> float | None:
        product = self.get_product_by_id(product_id)

        if product is None:
            return None

        return float(product["price_brl"])
