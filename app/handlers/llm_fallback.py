import logging
from aiogram import types
from openai import AsyncOpenAI, OpenAIError
from config import settings
from app.database.state_store import state_store

logger = logging.getLogger(__name__)

# Initialize Asynchronous OpenAI Client safely
try:
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI Client: {e}")
    openai_client = None

async def handle_llm_fallback(message: types.Message):
    """Processes message through the LLM pipeline with explicit runtime fallbacks."""
    user_id = str(message.from_user.id)
    user_text = message.text

    if not openai_client or not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        await message.reply("⚠️ AI Engine is unconfigured. Please check back later.")
        return

    # Show a typing indicator to the user while processing asynchronously
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # 1. Fetch Session from SQLite DB
    session = state_store.get_session(user_id)
    history = session["chat_history"]

    # 2. Append incoming message to history
    history.append({"role": "user", "content": user_text})

    # 3. Construct System Prompt to enforce strict boundaries
    system_prompt = {
        "role": "system",
        "content": "You are a professional, helpful conversational messaging assistant. Keep responses brief, scannable, and under 3 structural sentences when possible."
    }
    
    messages_payload = [system_prompt] + history

    try:
        # 4. Asynchronous API payload call
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_payload,
            max_tokens=250,
            temperature=0.7,
            timeout=10.0
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # 5. Save the system model's answer back to memory
        history.append({"role": "assistant", "content": bot_response})
        state_store.update_session(user_id, state="CONVERSING", history=history)

        # 6. Deliver the sanitized message response
        await message.answer(bot_response)

    except OpenAIError as oie:
        logger.error(f"OpenAI API Failure for user {user_id}: {oie}")
        await message.reply("🤖 I am experiencing trouble connecting to my brain systems. Please try again in a moment.")
    except Exception as e:
        logger.critical(f"Unexpected silent error in fallback runner: {str(e)}")
        await message.reply("🔧 An internal application processing error occurred. Flow reset.")
