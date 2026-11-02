
import json

from langchain_core.tools import tool

from app.services.store_service import StoreService


store = StoreService()


def serialize_result(data) -> str:
    return json.dumps(
        data,
        ensure_ascii=False,
        default=str,
    )


@tool(
    "search_products",
    description=(
        "Pesquisa produtos no catálogo pelo nome ou descrição. "
        "Use available_only=True quando o cliente procurar "
        "produtos disponíveis, em estoque ou para comprar. "
        "Use available_only=False quando quiser pesquisar "
        "todo o catálogo, inclusive produtos indisponíveis."
    ),
)
def search_products(
    query: str,
    limit: int = 5,
    available_only: bool = False,
) -> str:

    products = store.search_products(
        query=query,
        limit=limit,
        available_only=available_only,
    )

    safe_products = []

    for product in products:
        safe_products.append({
            "product_id": int(product["product_id"]),
            "name": str(product["name"]),
            "description": str(product["description"]),
            "price_brl": float(product["price_brl"]),
            "stock_quantity": int(product["stock_quantity"]),
            "status": str(product["status"]),
        })

    return serialize_result({
        "found": bool(safe_products),
        "count": len(safe_products),
        "products": safe_products,
    })


@tool(
    "get_product_details",
    description="Consulta os detalhes de um produto pelo seu ID.",
)
def get_product_details(product_id: int) -> str:

    product = store.get_product(product_id)

    if product is None:
        return serialize_result({
            "found": False,
            "message": "Produto não encontrado.",
        })

    return serialize_result({
        "found": True,
        "product": {
            "product_id": int(product["product_id"]),
            "name": str(product["name"]),
            "description": str(product["description"]),
            "price_brl": float(product["price_brl"]),
            "stock_quantity": int(product["stock_quantity"]),
            "status": str(product["status"]),
            "specs": str(product["specs"]),
        },
    })


@tool(
    "get_product_price_options",
    description=(
        "Consulta o preço, promoções e condições de pagamento "
        "via PIX de um produto. Use para perguntas sobre valores."
    ),
)
def get_product_price_options(product_id: int) -> str:

    options = store.get_product_price_options(product_id)

    if options is None:
        return serialize_result({
            "found": False,
            "message": "Produto não encontrado.",
        })

    product = store.get_product(product_id)

    return serialize_result({
        "found": True,
        "product_name": product["name"],
        "price_options": options,
    })


@tool(
    "search_store_policy",
    description=(
        "Pesquisa no manual de políticas da loja. "
        "Use para dúvidas sobre horários, frete, entregas, "
        "trocas, devoluções, pagamentos e garantias."
    ),
)
def search_store_policy(question: str) -> str:

    result = store.search_policy(
        question=question,
        top_k=3,
    )

    return serialize_result(result)


STORE_TOOLS = [
    search_products,
    get_product_details,
    get_product_price_options,
    search_store_policy,
]
