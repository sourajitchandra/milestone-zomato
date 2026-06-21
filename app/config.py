"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv()

_DEFAULT_DATASET = "ManikaSaini/zomato-restaurant-recommendation"
_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


class Settings(BaseModel):
    """Typed settings for the restaurant recommendation service."""

    hf_dataset_name: str = Field(default=_DEFAULT_DATASET)
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default=_DEFAULT_MODEL)
    groq_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    groq_max_tokens: int = Field(default=1024, ge=1)
    max_candidates: int = Field(default=50, ge=1)
    default_top_n: int = Field(default=5, ge=1, le=10)
    budget_low_max: int = Field(default=500, ge=0)
    budget_medium_max: int = Field(default=1500, ge=0)

    @field_validator("hf_dataset_name", "groq_model")
    @classmethod
    def strip_non_empty_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value cannot be empty")
        return stripped

    @model_validator(mode="after")
    def validate_budget_tiers(self) -> Settings:
        if self.budget_low_max >= self.budget_medium_max:
            raise ValueError(
                "BUDGET_LOW_MAX must be less than BUDGET_MEDIUM_MAX"
            )
        return self

    def require_groq_api_key(self) -> None:
        """Raise a clear error when Groq credentials are missing."""
        if not self.groq_api_key.strip():
            raise ValueError(
                "GROQ_API_KEY is not configured. "
                "Copy .env.example to .env and add your key from "
                "https://console.groq.com/keys"
            )

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings from the environment."""
    return Settings(
        hf_dataset_name=os.getenv("HF_DATASET_NAME", _DEFAULT_DATASET).strip(),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", _DEFAULT_MODEL).strip(),
        groq_temperature=_env_float("GROQ_TEMPERATURE", 0.3),
        groq_max_tokens=_env_int("GROQ_MAX_TOKENS", 1024),
        max_candidates=_env_int("MAX_CANDIDATES", 50),
        default_top_n=_env_int("DEFAULT_TOP_N", 5),
        budget_low_max=_env_int("BUDGET_LOW_MAX", 500),
        budget_medium_max=_env_int("BUDGET_MEDIUM_MAX", 1500),
    )
