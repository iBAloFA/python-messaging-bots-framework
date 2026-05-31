# app/discord_main.py
import discord
import logging
import os
from app.handlers.llm_engine import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure secure intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read text arrays

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"Successfully authenticated Discord interface layer as: {client.user}")

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself to prevent infinite feedback loops
    if message.author == client.user:
        return

    # Trigger typing indicator to mimic processing latency
    async with message.channel.typing():
        user_id = f"discord_{message.author.id}"
        ai_reply = await get_ai_response(user_id, message.content)
        await message.channel.send(ai_reply)

if __name__ == "__main__":
    # Pull token directly from global OS environments securely
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        logger.error("Failed to boot Discord Engine: DISCORD_TOKEN missing from environment settings.")
