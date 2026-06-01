# app/handlers/commands.py
from aiogram import types
from app.database.state_store import state_store

async def cmd_start(message: types.Message):
    user_id = f"tg_{message.from_user.id}"
    state_store.update_session(user_id, state="START", history=[])
    
    welcome_text = (
        "🌲 **Welcome to the Python Messaging Bot Framework!**\n\n"
        "This system features multi-platform routing pipelines and stable SQLite state engines.\n\n"
        "💬 *Send any plain text to converse with the core fallback AI!*"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

async def cmd_help(message: types.Message):
    help_text = "🛠️ **Available Core Sub-Commands:**\n\n/start - Reset interface\n/help - View schema details\n/reset - Wipe memory logs"
    await message.answer(help_text, parse_mode="Markdown")

async def cmd_reset(message: types.Message):
    user_id = f"tg_{message.from_user.id}"
    state_store.clear_session(user_id)
    await message.answer("🧹 *Session scratchpad memory successfully cleared.*", parse_mode="Markdown")
