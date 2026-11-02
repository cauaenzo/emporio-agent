
import json
import unicodedata

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.agent.llm_factory import create_llm
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import STORE_TOOLS


class StoreAgent:

    MAX_ITERATIONS = 5

    ADDITIONAL_LOOKUP_TERMS = {
        "horario",
        "funcionamento",
        "frete",
        "entrega",
        "troca",
        "devolucao",
        "garantia",
        "parcelamento",
        "acessorios",
        "politica",
        "prazo",
        "reclamacao",
        "atendimento",
        "endereco",
        "contato",
        "expediente",
        "feriado",
        "estoque",
        "disponivel",
        "disponibilidade",
        "quantidade",
        "caracteristicas",
        "descricao",
        "especificacoes",
    }

    def __init__(self):
        self.llm = create_llm().bind_tools(STORE_TOOLS)

        self.tools = {
            tool.name: tool
            for tool in STORE_TOOLS
        }

        self.history = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]

    @staticmethod
    def normalize_text(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)

        return "".join(
            char
            for char in value
            if not unicodedata.combining(char)
        ).casefold()

    def _requires_additional_lookup(self, question: str) -> bool:
        normalized = self.normalize_text(question)

        return any(
            term in normalized
            for term in self.ADDITIONAL_LOOKUP_TERMS
        )

    @staticmethod
    def format_brl(value: float) -> str:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "X")
        formatted = formatted.replace(".", ",")
        formatted = formatted.replace("X", ".")

        return f"R$ {formatted}"

    def format_price_response(self, results: list[dict]) -> str:
        responses = []

        for result in results:
            if not result.get("found"):
                responses.append(
                    "Não encontrei esse produto no catálogo."
                )
                continue

            name = result["product_name"]
            options = result["price_options"]

            base_price = self.format_brl(
                options["base_price"]
            )

            lines = [
                f"**{name}**",
                f"Preço normal: {base_price}",
            ]

            promotion = options.get("promotion")

            if promotion:
                promotional_price = self.format_brl(
                    promotion["promotional_price"]
                )

                lines.append(
                    f"Promoção: {promotion['discount_percent']}% "
                    "de desconto"
                )

                lines.append(
                    f"Preço promocional: {promotional_price}"
                )

                lines.append(
                    "O desconto de PIX não é acumulado com a promoção."
                )

            else:
                lines.append(
                    "Não há promoção ativa para este produto."
                )

                if options.get("pix_price") is not None:
                    pix_price = self.format_brl(
                        options["pix_price"]
                    )

                    lines.append(
                        f"Preço via PIX: {pix_price}"
                    )

            responses.append("\n".join(lines))

        return "\n\n".join(responses)

    def ask(self, question: str) -> str:
        if not question or not question.strip():
            return "Por favor, digite uma pergunta."

        question = question.strip()

        messages = self.history + [
            HumanMessage(content=question)
        ]

        for _ in range(self.MAX_ITERATIONS):
            response = self.llm.invoke(messages)

            messages.append(response)

            if not response.tool_calls:
                answer = response.content

                if isinstance(answer, list):
                    answer = " ".join(
                        str(part.get("text", ""))
                        for part in answer
                        if isinstance(part, dict)
                    )

                if not answer:
                    answer = (
                        "Não consegui formular uma resposta. "
                        "Pode reformular sua pergunta?"
                    )

                self.history = messages

                return str(answer)

            price_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                selected_tool = self.tools.get(tool_name)

                if selected_tool is None:
                    result = {
                        "error": "Ferramenta não encontrada."
                    }
                else:
                    try:
                        result = selected_tool.invoke(tool_args)

                    except Exception as error:
                        result = {
                            "error": "Não foi possível executar a consulta.",
                            "type": type(error).__name__,
                        }

                if tool_name == "get_product_price_options":
                    try:
                        if isinstance(result, str):
                            price_results.append(json.loads(result))
                        else:
                            price_results.append(result)

                    except (TypeError, json.JSONDecodeError):
                        price_results.append({
                            "found": False,
                        })

                if not isinstance(result, str):
                    result = json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    )

                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_id,
                    )
                )

            if (
                price_results
                and len(response.tool_calls) == 1
                and not self._requires_additional_lookup(question)
            ):
                answer = self.format_price_response(price_results)

                messages.append(
                    AIMessage(content=answer)
                )

                self.history = messages

                return answer

        answer = (
            "Não consegui concluir sua solicitação dentro "
            "do limite de consultas. Tente reformular a pergunta."
        )

        self.history = messages

        return answer
