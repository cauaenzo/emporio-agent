from langchain_openai import ChatOpenAI

from app.config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    validate_llm_config,
)


def create_llm():


    validate_llm_config()

    if LLM_PROVIDER == "openai-compatible":
        return ChatOpenAI(
            model=LLM_MODEL,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=LLM_TEMPERATURE,
            timeout=60,
            max_retries=2,
        )

    raise ValueError(
        f"Provedor não suportado: {LLM_PROVIDER}. "
        "Utilize 'openai-compatible' ou implemente "
        "um adaptador específico."
    )