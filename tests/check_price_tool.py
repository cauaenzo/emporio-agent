
from app.agent.tools import get_product_price_options


def main():
    product_ids = [84, 88]

    for product_id in product_ids:
        print("\n" + "=" * 50)
        print(f"Produto ID: {product_id}")
        print("=" * 50)

        result = get_product_price_options.invoke({
            "product_id": product_id
        })

        print(result)


if __name__ == "__main__":
    main()
