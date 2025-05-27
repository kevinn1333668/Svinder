from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    LLM_TOKEN: str
    ADMIN_TOKEN: str

    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    JWT_SECRET: str
    
    ADMIN_ID: int

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@db:5432/{self.DB_NAME}"
        )
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()