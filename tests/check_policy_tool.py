
from app.agent.tools import search_store_policy


def main():
    questions = [
        "A loja vende acessórios?",
        "Qual é o horário de funcionamento?",
        "Como funciona a política de troca?",
        "Existe frete grátis?",
    ]

    for question in questions:
        print("\n" + "=" * 60)
        print(f"Pergunta: {question}")
        print("=" * 60)

        result = search_store_policy.invoke({
            "question": question
        })

        print(result)


if __name__ == "__main__":
    main()
