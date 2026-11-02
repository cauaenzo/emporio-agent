
from decimal import Decimal, ROUND_HALF_UP


class StoreRules:
    PIX_DISCOUNT = Decimal("0.05")
    FREE_SHIPPING_MINIMUM = Decimal("500.00")
    SHIPPING_FEE = Decimal("35.00")
    MAX_INSTALLMENTS = 12

    @classmethod
    def calculate_pix_price(cls, price: float) -> Decimal:
        value = Decimal(str(price))

        if value < 0:
            raise ValueError("O preço não pode ser negativo.")

        discounted = value * (1 - cls.PIX_DISCOUNT)

        return discounted.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @classmethod
    def calculate_shipping(cls, order_total: float) -> Decimal:
        value = Decimal(str(order_total))

        if value < 0:
            raise ValueError(
                "O valor do pedido não pode ser negativo."
            )

        if value > cls.FREE_SHIPPING_MINIMUM:
            return Decimal("0.00")

        return cls.SHIPPING_FEE

    @classmethod
    def calculate_installment(
        cls,
        total: float,
        installments: int,
    ) -> Decimal:
        value = Decimal(str(total))

        if value < 0:
            raise ValueError("O total não pode ser negativo.")

        if not 1 <= installments <= cls.MAX_INSTALLMENTS:
            raise ValueError("Quantidade de parcelas inválida.")

        return (value / installments).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
