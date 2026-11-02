
from app.agent.agent import StoreAgent


SCENARIOS = [
    {
        "name": "Pesquisa de produtos",
        "questions": [
            "Quais violões Giannini estão disponíveis?",
            "Quais violões de nylon vocês possuem?",
            "Vocês têm Yamaha C40?",
        ],
    },
    {
        "name": "Continuidade da conversa",
        "questions": [
            "Quais são os violões Giannini disponíveis?",
            "Quanto custa o GN-15 no PIX?",
            "E o GF-1R?",
        ],
    },
    {
        "name": "Produto inexistente",
        "questions": [
            "Vocês têm o violão modelo XYZ-999?",
            "Quanto custa esse produto?",
        ],
    },
    {
        "name": "Promoções e descontos",
        "questions": [
            "O GN-15 está em promoção?",
            "Posso acumular o desconto da promoção com o PIX?",
        ],
    },
    {
        "name": "Consulta ao manual",
        "questions": [
            "Qual é o horário de funcionamento da loja?",
            "Vocês vendem palhetas e cabos?",
            "Quantos dias tenho para devolver uma compra online?",
        ],
    },
    {
        "name": "Frete",
        "questions": [
            "A partir de qual valor o frete é gratuito?",
            "E se minha compra for de R$ 400?",
            "E se minha compra for exatamente R$ 500?",
        ],
    },
    {
        "name": "Consulta combinada",
        "questions": [
            "Qual é o preço do GN-15 no PIX e qual é o horário de funcionamento da loja?",
        ],
    },
    {
        "name": "Limite de atendimento",
        "questions": [
            "Qual é a capital da França?",
            "Quem ganhou a última Copa do Mundo?",
        ],
    },
]


def main():
    for index, scenario in enumerate(SCENARIOS, start=1):
        print("\n" + "=" * 70)
        print(f"CENÁRIO {index}: {scenario['name']}")
        print("=" * 70)

        agent = StoreAgent()

        for question in scenario["questions"]:
            print(f"\nCliente: {question}")

            try:
                response = agent.ask(question)
                print(f"\nAssistente: {response}")

            except Exception as error:
                print("\nErro ao executar a consulta.")
                print(f"Tipo: {type(error).__name__}")
                print(f"Detalhes: {error}")

        print()


if __name__ == "__main__":
    main()
