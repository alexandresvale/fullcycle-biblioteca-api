from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FullCycle Biblioteca API"
    app_version: str = "0.1.0"
    app_description: str = "API de Biblioteca (Projeto B) - Acervo e Emprestimos"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://biblioteca:biblioteca@db:5432/biblioteca"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
