from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEOID_PATH: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()