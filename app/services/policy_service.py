
from app.rag.retriever import PolicyRetriever


class PolicyService:
    """Disponibiliza consultas ao manual de políticas da loja."""

    def __init__(self):
        self.retriever = PolicyRetriever()
        self.retriever.load_index()

    def search_policy(
        self,
        question: str,
        top_k: int = 3,
    ) -> dict:

        if not question or not question.strip():
            return {
                "found": False,
                "question": question,
                "results": [],
            }

        results = self.retriever.search(
            query=question,
            top_k=top_k,
        )

        if not results:
            return {
                "found": False,
                "question": question,
                "results": [],
            }

        formatted_results = []

        for result in results:
            formatted_results.append({
                "text": result["text"],
                "pages": result["pages"],
                "relevance_score": round(
                    float(result["score"]),
                    5,
                ),
            })

        return {
            "found": True,
            "question": question,
            "results": formatted_results,
        }
