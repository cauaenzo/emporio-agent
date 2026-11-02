
import pytest

from app.rag.retriever import PolicyRetriever


@pytest.fixture(scope="module")
def retriever():
    instance = PolicyRetriever()
    instance.build_index()
    return instance


@pytest.mark.parametrize(
    "question, expected_terms",
    [
        (
            "Em quais dias e horários a loja funciona?",
            ["segunda a sexta-feira", "09:00 às 18:00"],
        ),
        (
            "Quantos dias tenho para devolver uma compra feita pela internet?",
            ["7 (sete) dias corridos", "recebimento do produto"],
        ),
        (
            "A partir de qual valor o frete é gratuito?",
            ["frete grátis", "R$ 500,00"],
        ),
        (
            "Qual é o desconto oferecido para pagamento via PIX?",
            ["PIX", "5% de desconto"],
        ),
        (
            "Em quantas vezes posso parcelar uma compra no cartão?",
            ["12x sem juros", "R$ 100,00"],
        ),
        (
            "A loja vende acessórios?",
            ["não comercializamos acessórios"],
        ),
    ],
)
def test_retrieval_finds_expected_information(
    retriever,
    question,
    expected_terms,
):
    results = retriever.search(question, top_k=3)

    retrieved_text = " ".join(
        result["text"] for result in results
    ).lower()

    for term in expected_terms:
        assert term.lower() in retrieved_text, (
            f"Informação esperada não encontrada: {term}\n"
            f"Pergunta: {question}"
        )
