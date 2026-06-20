from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY:str
    OPENAI_API_BASE_URL:str
    LLM_MODEL_NAME: str

settings = Settings()