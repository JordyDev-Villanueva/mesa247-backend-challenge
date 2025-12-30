from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://mesa247:mesa247_dev@localhost:5432/mesa247_db"

    # Application
    APP_NAME: str = "Mesa247 Backend Challenge"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_PREFIX: str = "/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
