from app.rag.ingestion import PDFIngestion


def main():
    ingestion = PDFIngestion()
    chunks = ingestion.create_chunks()

    print(f"Total de chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 90)
        print(f"CHUNK {index}")
        print(f"Páginas: {chunk['pages']}")
        print(f"Quantidade de palavras: {len(chunk['text'].split())}")
        print("-" * 90)
        print(chunk["text"])


if __name__ == "__main__":
    main()