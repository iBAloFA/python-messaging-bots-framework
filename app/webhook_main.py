import asyncio
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from config import settings

from app.handlers.commands import cmd_start, cmd_help, cmd_reset
from app.handlers.llm_fallback import handle_llm_fallback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Initialize Core App Components
bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Define your secure webhook endpoint suffix
WEBHOOK_PATH = f"/webhook/tg/{settings.bot_token[:10]}"
# Replace this with your actual Ngrok URL or production domain!
BASE_URL = "https://ngrok-free.app" 
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

fastapi_app = FastAPI()

# 2. Register Bot Routes
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_help, Command("help"))
dp.message.register(cmd_reset, Command("reset"))
dp.message.register(handle_llm_fallback, F.text)

@fastapi_app.on_event("startup")
async def on_startup():
    """Tells Telegram where to send message payloads when the server boots."""
    logger.info(f"Setting webhook target to: {WEBHOOK_URL}")
    await bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message"]
    )

@fastapi_app.post(WEBHOOK_PATH)
async def telegram_webhook_endpoint(request: Request):
    """Receives incoming JSON updates from Telegram and feeds them to the Async Event Loop."""
    try:
        json_data = await request.json()
        update = types.Update(**json_data)
        await dp.feed_update(bot, update)
        return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error handling webhook payload: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@fastapi_app.on_event("shutdown")
async def on_shutdown():
    """Gracefully closes network connections on shutdown."""
    logger.info("Tearing down server sessions...")
    await bot.delete_webhook()
    await bot.session.close()

# To run this server: pip install uvicorn fastapi
# Execute: uvicorn app.webhook_main:fastapi_app --host 0.0.0.0 --port 8080
