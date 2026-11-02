
from app.rag.retriever import PolicyRetriever


def main():
    retriever = PolicyRetriever()

    print("Construindo índices de busca...")

    total_chunks = retriever.build_index()
    retriever.save_index()

    print(f"Chunks indexados: {total_chunks}")

    questions = [
        "Em quais dias e horários a loja funciona?",
        "Quantos dias tenho para devolver uma compra feita pela internet?",
        "A partir de qual valor o frete é gratuito?",
        "Qual é o desconto oferecido para pagamento via PIX?",
        "Em quantas vezes posso parcelar uma compra no cartão?",
        "A loja vende acessórios?",
    ]

    for question in questions:
        print("\n" + "=" * 80)
        print(f"Pergunta: {question}")

        results = retriever.search(
            question,
            top_k=3,
        )

        if not results:
            print("Nenhum resultado encontrado.")
            continue

        for result in results:
            print(f"\nPáginas: {result['pages']}")
            print(f"RRF: {result['score']:.5f}")
            print(f"Semântica: {result['dense_score']:.4f}")
            print(f"Palavras: {result['word_score']:.4f}")
            print(f"Caracteres: {result['char_score']:.4f}")
            print("-" * 50)
            print(result["text"][:700])


if __name__ == "__main__":
    main()
