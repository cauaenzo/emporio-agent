import pandas as pd

from app.config import DATA_FILES


class CustomerDirectory:
    """Realiza verificações básicas de existência de clientes."""

    def __init__(self):
        # Carrega somente o ID, evitando armazenar dados pessoais
        self.customers = pd.read_csv(
            DATA_FILES["customers"],
            usecols=["customer_id"],
        )

        self._validate_data()

    def _validate_data(self):
        if self.customers["customer_id"].duplicated().any():
            raise ValueError("Existem IDs de clientes duplicados.")

    def customer_exists(self, customer_id: int) -> bool:
        """Verifica se um ID está cadastrado."""

        if customer_id <= 0:
            return False

        return bool(
            (self.customers["customer_id"] == customer_id).any()
        )