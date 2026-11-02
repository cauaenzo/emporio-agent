
from app.agent.agent import StoreAgent


def main():
    print("=" * 55)
    print("       EMPÓRIO DA MÚSICA - ASSISTENTE VIRTUAL")
    print("=" * 55)
    print("Digite sua pergunta ou 'sair' para encerrar.")
    print()

    try:
        agent = StoreAgent()

        print("Assistente inicializado com sucesso.\n")

        while True:
            question = input("Você: ").strip()

            if question.lower() in {"sair", "exit", "quit"}:
                print("\nAtendimento encerrado.")
                break

            if not question:
                continue

            try:
                response = agent.ask(question)

                print(f"\nAssistente: {response}\n")

            except Exception as error:
                print("\nOcorreu um erro ao processar sua pergunta.")
                print(f"Tipo: {type(error).__name__}\n")

    except Exception as error:
        print("Não foi possível inicializar o assistente.")
        print(f"Tipo: {type(error).__name__}")


if __name__ == "__main__":
    main()
