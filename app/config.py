
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


# Configurações gerais
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"


# Configurações independentes do provedor de LLM
LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openai-compatible",
).lower()

LLM_API_KEY = os.getenv("LLM_API_KEY")

LLM_BASE_URL = os.getenv("LLM_BASE_URL") or None

LLM_MODEL = os.getenv("LLM_MODEL")

LLM_TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", "0")
)


# Diretórios
def resolve_directory(value: str) -> Path:
    path = Path(value)

    return path if path.is_absolute() else BASE_DIR / path


DATA_DIR = resolve_directory(
    os.getenv("DATA_DIR", "data/private")
)

VECTOR_STORE_DIR = resolve_directory(
    os.getenv("VECTOR_STORE_DIR", "storage/faiss")
)


# Arquivos do desafio
DATA_FILES = {
    "products": DATA_DIR / "desafio_tecnico_ai_eng - products.csv",
    "categories": DATA_DIR / "desafio_tecnico_ai_eng - categories.csv",
    "customers": DATA_DIR / "desafio_tecnico_ai_eng - customers.csv",
    "orders": DATA_DIR / "desafio_tecnico_ai_eng - orders.csv",
    "order_items": DATA_DIR / "desafio_tecnico_ai_eng - order_items.csv",
    "promotions": DATA_DIR / "desafio_tecnico_ai_eng - promotions.csv",
    "policies": DATA_DIR / "políticas_da_loja.pdf",
}


def validate_data_files() -> list[str]:
    return [
        name
        for name, path in DATA_FILES.items()
        if not path.is_file()
    ]


def validate_llm_config() -> None:
    if not LLM_API_KEY:
        raise ValueError(
            "LLM_API_KEY não encontrada. Confira o arquivo .env."
        )

    if not LLM_MODEL:
        raise ValueError(
            "LLM_MODEL não foi configurado."
        )

    if LLM_TEMPERATURE < 0:
        raise ValueError(
            "LLM_TEMPERATURE não pode ser negativa."
        )
