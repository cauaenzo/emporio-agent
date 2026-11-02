from app.agent.llm_factory import create_llm


def main():
    print("Inicializando modelo...")

    try:
        llm = create_llm()

        print("Modelo inicializado.")
        print("Enviando mensagem para a API...")

        response = llm.invoke(
            "Responda em português, apenas: "
            "Conexão com o modelo realizada com sucesso."
        )

        print("\nResposta do modelo:")
        print(response.content)

    except Exception as error:
        print("\nNão foi possível concluir o teste.")
        print(f"Tipo do erro: {type(error).__name__}")
        print(
            "Confira as configurações do .env, "
            "a disponibilidade do modelo e os limites da API."
        )


if __name__ == "__main__":
    main()