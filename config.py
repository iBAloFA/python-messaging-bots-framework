import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    bot_token: str = Field(..., validation_alias="BOT_TOKEN")
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    database_url: str = Field("sqlite:///bot_memory.db", validation_alias="DATABASE_URL")
    
    # Add explicit fallback mapping for your Discord token setup
    discord_token: str = Field("mock_key", validation_alias="DISCORD_TOKEN")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

try:
    settings = Settings()
except Exception as e:
    print(f"Configuration Error: Ensure your .env file is configured properly.\nDetails: {e}")
    raise e
