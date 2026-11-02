
import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agent.agent import StoreAgent


class FakeLLM:
    def __init__(self, responses):
        self.responses = responses
        self.calls = 0
        self.message_history = []

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def invoke(self, messages):
        self.message_history.append(list(messages))
        response = self.responses[self.calls]
        self.calls += 1
        return response


class FakeTool:
    def __init__(self, name, result):
        self.name = name
        self.result = result
        self.received_args = None

    def invoke(self, args):
        self.received_args = args
        return self.result


class FailingTool:
    def __init__(self, name):
        self.name = name
        self.received_args = None

    def invoke(self, args):
        self.received_args = args
        raise RuntimeError("Falha simulada na ferramenta.")


def create_agent(monkeypatch, responses):
    fake_llm = FakeLLM(responses)

    monkeypatch.setattr(
        "app.agent.agent.create_llm",
        lambda: fake_llm,
    )

    return StoreAgent(), fake_llm


def test_agent_returns_model_response(monkeypatch):
    agent, fake_llm = create_agent(
        monkeypatch,
        [
            AIMessage(content="Olá! Como posso ajudar?"),
        ],
    )

    response = agent.ask("Olá")

    assert response == "Olá! Como posso ajudar?"
    assert fake_llm.calls == 1


def test_agent_formats_product_price(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_product_price_options",
                "args": {"product_id": 84},
                "id": "call_1",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [tool_call],
    )

    tool_result = {
        "found": True,
        "product_name": "Giannini GN-15 Nylon Cedr Natural",
        "price_options": {
            "base_price": 689.00,
            "promotion": None,
            "pix_price": 654.55,
        },
    }

    fake_tool = FakeTool(
        "get_product_price_options",
        json.dumps(tool_result),
    )

    agent.tools["get_product_price_options"] = fake_tool

    response = agent.ask("Quanto custa o GN-15 no PIX?")

    assert fake_tool.received_args == {"product_id": 84}
    assert "R$ 689,00" in response
    assert "R$ 654,55" in response
    assert "Giannini GN-15" in response
    assert fake_llm.calls == 1


def test_agent_handles_empty_question(monkeypatch):
    agent, fake_llm = create_agent(
        monkeypatch,
        [
            AIMessage(content="Resposta que não deveria ser usada."),
        ],
    )

    response = agent.ask("   ")

    assert response == "Por favor, digite uma pergunta."
    assert fake_llm.calls == 0


def test_agent_executes_policy_tool(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_store_policy",
                "args": {"question": "Qual o horário de funcionamento?"},
                "id": "call_2",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [
            tool_call,
            AIMessage(
                content="A loja funciona de segunda a sexta, das 9h às 18h."
            ),
        ],
    )

    fake_tool = FakeTool(
        "search_store_policy",
        json.dumps({
            "results": [
                {
                    "page": 2,
                    "content": "Segunda a sexta, das 09h às 18h.",
                }
            ]
        }),
    )

    agent.tools["search_store_policy"] = fake_tool

    response = agent.ask("Qual o horário de funcionamento?")

    assert fake_tool.received_args == {
        "question": "Qual o horário de funcionamento?"
    }
    assert "segunda a sexta" in response
    assert fake_llm.calls == 2


def test_agent_handles_out_of_scope_question(monkeypatch):
    agent, fake_llm = create_agent(
        monkeypatch,
        [
            AIMessage(
                content="Meu atendimento é limitado aos assuntos do Empório da Música."
            ),
        ],
    )

    response = agent.ask("Qual é a capital da França?")

    assert "limitado" in response
    assert fake_llm.calls == 1


def test_agent_formats_promotional_price(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_product_price_options",
                "args": {"product_id": 84},
                "id": "call_3",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [tool_call],
    )

    tool_result = {
        "found": True,
        "product_name": "Giannini GN-15 Nylon Cedr Natural",
        "price_options": {
            "base_price": 689.00,
            "promotion": {
                "discount_percent": 10,
                "promotional_price": 620.10,
            },
            "pix_price": None,
        },
    }

    fake_tool = FakeTool(
        "get_product_price_options",
        json.dumps(tool_result),
    )

    agent.tools["get_product_price_options"] = fake_tool

    response = agent.ask("O GN-15 está em promoção?")

    assert "R$ 689,00" in response
    assert "10%" in response
    assert "R$ 620,10" in response
    assert "R$ 654,55" not in response
    assert fake_llm.calls == 1


def test_agent_handles_nonexistent_product_price(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_product_price_options",
                "args": {"product_id": 9999},
                "id": "call_4",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [tool_call],
    )

    fake_tool = FakeTool(
        "get_product_price_options",
        json.dumps({
            "found": False,
            "message": "Produto não encontrado.",
        }),
    )

    agent.tools["get_product_price_options"] = fake_tool

    response = agent.ask("Quanto custa o produto 9999?")

    assert "Não encontrei esse produto" in response
    assert fake_tool.received_args == {"product_id": 9999}
    assert fake_llm.calls == 1


def test_agent_preserves_conversation_history(monkeypatch):
    agent, fake_llm = create_agent(
        monkeypatch,
        [
            AIMessage(content="Olá! Como posso ajudar?"),
            AIMessage(content="Temos o violão Giannini GN-15."),
        ],
    )

    first_response = agent.ask("Olá")
    second_response = agent.ask("Quais violões vocês têm?")

    assert first_response == "Olá! Como posso ajudar?"
    assert second_response == "Temos o violão Giannini GN-15."

    second_call_messages = fake_llm.message_history[1]

    assert isinstance(second_call_messages[1], HumanMessage)
    assert second_call_messages[1].content == "Olá"

    assert second_call_messages[2].content == "Olá! Como posso ajudar?"

    assert isinstance(second_call_messages[3], HumanMessage)
    assert second_call_messages[3].content == "Quais violões vocês têm?"


def test_agent_handles_tool_execution_error(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_store_policy",
                "args": {"question": "Qual o horário?"},
                "id": "call_5",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [
            tool_call,
            AIMessage(content="Não consegui consultar o manual neste momento."),
        ],
    )

    failing_tool = FailingTool("search_store_policy")
    agent.tools["search_store_policy"] = failing_tool

    response = agent.ask("Qual o horário?")

    assert failing_tool.received_args == {"question": "Qual o horário?"}
    assert "Não consegui consultar" in response
    assert fake_llm.calls == 2

    tool_message = next(
        message
        for message in fake_llm.message_history[1]
        if isinstance(message, ToolMessage)
    )

    assert "Não foi possível executar a consulta." in tool_message.content
    assert "RuntimeError" in tool_message.content


def test_agent_handles_unknown_tool(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "unknown_tool",
                "args": {},
                "id": "call_6",
                "type": "tool_call",
            }
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [
            tool_call,
            AIMessage(content="Não consegui realizar essa consulta."),
        ],
    )

    response = agent.ask("Faça uma consulta.")

    assert response == "Não consegui realizar essa consulta."
    assert fake_llm.calls == 2

    tool_message = next(
        message
        for message in fake_llm.message_history[1]
        if isinstance(message, ToolMessage)
    )

    assert "Ferramenta não encontrada." in tool_message.content


def test_agent_processes_multiple_tools(monkeypatch):
    tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_product_price_options",
                "args": {"product_id": 84},
                "id": "call_7",
                "type": "tool_call",
            },
            {
                "name": "search_store_policy",
                "args": {"question": "Qual o horário de funcionamento?"},
                "id": "call_8",
                "type": "tool_call",
            },
        ],
    )

    agent, fake_llm = create_agent(
        monkeypatch,
        [
            tool_call,
            AIMessage(
                content=(
                    "O GN-15 custa R$ 689,00, com desconto via PIX "
                    "por R$ 654,55. A loja funciona das 9h às 18h."
                )
            ),
        ],
    )

    price_tool = FakeTool(
        "get_product_price_options",
        json.dumps({
            "found": True,
            "product_name": "Giannini GN-15",
            "price_options": {
                "base_price": 689.00,
                "promotion": None,
                "pix_price": 654.55,
            },
        }),
    )

    policy_tool = FakeTool(
        "search_store_policy",
        json.dumps({
            "results": [
                {
                    "page": 2,
                    "content": "A loja funciona das 09h às 18h.",
                }
            ]
        }),
    )

    agent.tools["get_product_price_options"] = price_tool
    agent.tools["search_store_policy"] = policy_tool

    response = agent.ask(
        "Qual o preço do GN-15 no PIX e o horário da loja?"
    )

    assert price_tool.received_args == {"product_id": 84}

    assert policy_tool.received_args == {
        "question": "Qual o horário de funcionamento?"
    }

    assert "R$ 689,00" in response
    assert "R$ 654,55" in response
    assert "9h às 18h" in response
    assert fake_llm.calls == 2
