from aiogram import types
from aiogram.filters import Command
from app.database.state_store import state_store

async def cmd_start(message: types.Message):
    """Greets the user and boots their local state payload."""
    user_id = str(message.from_user.id)
    state_store.clear_session(user_id) # Fresh instantiation
    
    welcome_text = (
        f"👋 Hello, {message.from_user.first_name}!\n\n"
        "Welcome to the **Tendem Framework Engine**. I am an AI-powered messaging bot.\n\n"
        "📌 **Available Actions:**\n"
        "• Talk to me normally to interact with the LLM.\n"
        "• Type /reset to purge your conversation data storage.\n"
        "• Type /help for details."
    )
    await message.answer(welcome_text, parse_mode="Markdown")

async def cmd_help(message: types.Message):
    """Returns application support parameters."""
    help_text = (
        "💡 **Help Center**\n\n"
        "This bot uses an asynchronous pipeline linked to a robust state persistence architecture.\n\n"
        "• **/start** - Boot up execution\n"
        "• **/reset** - Wipe application session memory"
    )
    await message.answer(help_text, parse_mode="Markdown")

async def cmd_reset(message: types.Message):
    """Clears persistence schema cache for targeted user ID."""
    user_id = str(message.from_user.id)
    state_store.clear_session(user_id)
    await message.answer("🔄 **Session memory wiped cleanly.** Your conversation has been completely reset.")
