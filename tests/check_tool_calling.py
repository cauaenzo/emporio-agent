from langchain_core.tools import tool

from app.agent.llm_factory import create_llm


@tool
def search_products(query: str) -> str:
    """
    Pesquisa produtos no catálogo da loja.

    Utilize esta ferramenta quando o cliente perguntar
    sobre instrumentos musicais ou produtos disponíveis.

    Args:
        query: Nome ou descrição do produto procurado.
    """

    return (
        f"Ferramenta acionada com sucesso. "
        f"Pesquisa recebida: {query}"
    )


def main():
    print("Inicializando modelo...")

    try:
        llm = create_llm()

        print("Modelo inicializado.")
        print("Vinculando ferramenta ao modelo...")

        llm_with_tools = llm.bind_tools([search_products])

        print("Ferramenta vinculada.")
        print("Enviando pergunta...")

        response = llm_with_tools.invoke(
            "Estou procurando um violão Yamaha. "
            "Pesquise no catálogo para mim."
        )

        print("\nResposta do modelo:")
        print(response.content)

        print("\nChamadas de ferramentas:")

        if response.tool_calls:
            for call in response.tool_calls:
                print(f"Ferramenta: {call['name']}")
                print(f"Argumentos: {call['args']}")
                print(f"ID: {call['id']}")
        else:
            print("O modelo não solicitou nenhuma ferramenta.")

    except Exception as error:
        print("\nFalha no teste de Tool Calling.")
        print(f"Tipo do erro: {type(error).__name__}")
        print(f"Mensagem: {error}")


if __name__ == "__main__":
    main()