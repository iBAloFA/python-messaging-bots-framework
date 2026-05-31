import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from config import settings

# Import routing dependencies explicitly
from app.handlers.commands import cmd_start, cmd_help, cmd_reset
from app.handlers.llm_fallback import handle_llm_fallback

# Setting up professional execution logging targets
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing Asynchronous Bot Polling Lifecycle...")

    # 1. Instantiate Core Bot Engine
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # 2. Register Native Commands
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_reset, Command("reset"))

    # 3. Register Global Text LLM Fallback Catch-All
    # This captures any generic message text that isn't caught by the commands above
    dp.message.register(handle_llm_fallback, F.text)

    # 4. Start Event Loop Execution
    try:
        # Skip accumulation of pending updates when server was offline
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Fatal Engine Panic inside Event Loop Router: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution gracefully terminated by operator.")
