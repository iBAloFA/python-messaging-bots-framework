# app/handlers/llm_engine.py
import logging
from openai import AsyncOpenAI, OpenAIError
from config import settings
from app.database.state_store import state_store

logger = logging.getLogger(__name__)

try:
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI Client layout: {e}")
    openai_client = None

async def get_ai_response(user_id: str, user_text: str) -> str:
    """Core processing unit. Feeds chat strings and records dialog arrays."""
    # Catch unconfigured keys safely before running live HTTP requests
    if not openai_client or settings.openai_api_key in ["mock_key", ""]:
        return "⚠️ The LLM processing engine is currently unconfigured or processing in mock mode."

    session = state_store.get_session(user_id)
    history = session["chat_history"]
    history.append({"role": "user", "content": user_text})

    system_prompt = {
        "role": "system",
        "content": "You are a professional assistant. Keep responses brief, scannable, and under 3 sentences."
    }
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt] + history,
            max_tokens=200,
            temperature=0.7,
            timeout=8.0  # Safe internal network timeout guard
        )
        bot_response = response.choices.message.content.strip()
        
        # Save structural context loops back to storage arrays
        history.append({"role": "assistant", "content": bot_response})
        state_store.update_session(user_id, state="CONVERSING", history=history)
        return bot_response

    except OpenAIError as e:
        logger.error(f"Graceful Catch - OpenAI Network Connection Issue: {e}")
        return "🤖 The AI core is experiencing local network latency. Please send your message again."
    except Exception as e:
        logger.critical(f"System logic tracking trap: {e}")
        return "🔧 Temporary backend synchronization issue. Session preserved."
