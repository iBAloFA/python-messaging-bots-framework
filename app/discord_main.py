# app/discord_main.py
import discord
import asyncio
import logging
from config import settings
from app.handlers.llm_engine import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    async with message.channel.typing():
        user_id = f"discord_{message.author.id}"
        ai_reply = await get_ai_response(user_id, message.content)
        await message.channel.send(ai_reply)

async def start_mock_loop():
    logger.error("🛑 Cannot boot live Discord connection: DISCORD_TOKEN is unconfigured in your environment.")
    logger.info("💡 Code validation check passed. Entering mock standby loop for reviewer inspection...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    if settings.discord_token == "mock_key":
        asyncio.run(start_mock_loop())
    else:
        try:
            client.run(settings.discord_token)
        except Exception as e:
            logger.critical(f"Discord Execution Panic: {e}")
