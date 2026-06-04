from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DeepAgents Chat"
    model_id: str = Field(default="gpt-4o-mini", alias="MODEL_ID")
    model_base_url: str = Field(default="https://api.openai.com/v1", alias="MODEL_BASE_URL")
    model_api_key: str | None = Field(default=None, alias="MODEL_API_KEY")
    model_temperature: float = Field(default=0.7, alias="MODEL_TEMPERATURE")
    cors_origins_raw: str = Field(default="http://127.0.0.1:5173", alias="CORS_ORIGINS")
    skills_enabled: bool = Field(default=True, alias="SKILLS_ENABLED")
    skills_dir: str = Field(default="skills", alias="SKILLS_DIR")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
