
import pytest

from app.services.policy_service import PolicyService


@pytest.fixture(scope="module")
def policy_service():
    return PolicyService()


def test_service_loads_index(policy_service):
    assert policy_service.retriever.index is not None
    assert len(policy_service.retriever.chunks) > 0


def test_search_policy_returns_results(policy_service):
    result = policy_service.search_policy(
        "Qual é o desconto para pagamento via PIX?"
    )

    assert result["found"] is True
    assert len(result["results"]) > 0

    retrieved_text = " ".join(
        item["text"] for item in result["results"]
    ).lower()

    assert "5%" in retrieved_text
    assert "pix" in retrieved_text


def test_search_policy_includes_page_reference(policy_service):
    result = policy_service.search_policy(
        "Qual é o horário de funcionamento?"
    )

    assert result["found"] is True

    for item in result["results"]:
        assert isinstance(item["pages"], list)
        assert len(item["pages"]) > 0


def test_search_policy_empty_question(policy_service):
    result = policy_service.search_policy("")

    assert result["found"] is False
    assert result["results"] == []


def test_search_policy_rejects_invalid_top_k(policy_service):
    with pytest.raises(ValueError):
        policy_service.search_policy(
            "Qual é o horário de funcionamento?",
            top_k=0,
        )
