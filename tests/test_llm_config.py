
import pytest

from app import config


def test_llm_provider_is_configured():
    assert config.LLM_PROVIDER
    assert isinstance(config.LLM_PROVIDER, str)


def test_llm_model_is_configured():
    assert config.LLM_MODEL
    assert isinstance(config.LLM_MODEL, str)


def test_validate_llm_config_accepts_valid_settings(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", "test-api-key")
    monkeypatch.setattr(config, "LLM_MODEL", "test-model")
    monkeypatch.setattr(config, "LLM_TEMPERATURE", 0.0)

    config.validate_llm_config()


def test_validate_llm_config_rejects_missing_api_key(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", None)
    monkeypatch.setattr(config, "LLM_MODEL", "test-model")

    with pytest.raises(ValueError, match="LLM_API_KEY"):
        config.validate_llm_config()


def test_validate_llm_config_rejects_missing_model(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", "test-api-key")
    monkeypatch.setattr(config, "LLM_MODEL", None)

    with pytest.raises(ValueError, match="LLM_MODEL"):
        config.validate_llm_config()
