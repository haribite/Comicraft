from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    image_backend: str = "placeholder"
    panel_count: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
