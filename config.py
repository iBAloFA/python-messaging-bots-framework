# config.py
import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Safe default strings to prevent Pydantic validation panics if .env is missing
    bot_token: str = "MOCK_TELEGRAM_TOKEN_12345"
    openai_api_key: str = "mock_key"
    database_url: str = "sqlite:///bot_memory.db"
    discord_token: str = "mock_key"
    whatsapp_api_token: str = "mock_key"
    phone_number_id: str = "mock_id"
    whatsapp_verify_token: str = "SeyiSecureToken1234"

    # Instructs Pydantic to quietly check for a local file without requiring it
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

try:
    settings = Settings()
    if not os.path.exists(".env"):
        logger.warning("⚠️ No .env file detected locally. Deploying safe fallback configurations.")
except Exception as e:
    logger.critical(f"Configuration Critical Failure, creating structural backups: {e}")
    class BackupSettings:
        bot_token = "MOCK_TELEGRAM_TOKEN_12345"
        openai_api_key = "mock_key"
        database_url = "sqlite:///bot_memory.db"
        discord_token = "mock_key"
        whatsapp_api_token = "mock_key"
        phone_number_id = "mock_id"
        whatsapp_verify_token = "SeyiSecureToken1234"
    settings = BackupSettings()
