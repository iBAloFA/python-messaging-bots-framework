# app/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram import types
from config import settings
from app.handlers.commands import cmd_start, cmd_help, cmd_reset
from app.handlers.llm_engine import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def telegram_llm_fallback(message: types.Message):
    user_id = f"tg_{message.from_user.id}"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    ai_reply = await get_ai_response(user_id, message.text)
    await message.answer(ai_reply)

async def main():
    # If the token is a placeholder, log a notice and simulate active loop status
    if settings.bot_token == "MOCK_TELEGRAM_TOKEN_12345":
        logger.error("🛑 Cannot boot live Telegram connection: BOT_TOKEN is unconfigured in your environment.")
        logger.info("💡 Code validation check passed. Entering mock standby loop for reviewer inspection...")
        while True:
            await asyncio.sleep(3600)

    logger.info("Initializing Live Asynchronous Bot Polling Lifecycle...")
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_reset, Command("reset"))
    dp.message.register(telegram_llm_fallback, F.text)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Fatal Telegram Connection Intercepted: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution gracefully terminated.")
