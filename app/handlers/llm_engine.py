import logging
from openai import AsyncOpenAI, OpenAIError
from config import settings
from app.database.state_store import state_store

logger = logging.getLogger(__name__)

try:
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI Client: {e}")
    openai_client = None

async def get_ai_response(user_id: str, user_text: str) -> str:
    """Core platform-agnostic AI processor. Returns a raw response string."""
    if not openai_client or not settings.openai_api_key or settings.openai_api_key == "mock_key":
        return "⚠️ AI Engine is currently unconfigured."

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
            max_tokens=250,
            temperature=0.7,
            timeout=10.0
        )
        bot_response = response.choices.message.content.strip()
        
        history.append({"role": "assistant", "content": bot_response})
        state_store.update_session(user_id, state="CONVERSING", history=history)
        return bot_response

    except OpenAIError as e:
        logger.error(f"OpenAI Error: {e}")
        return "🤖 Internal AI connection timeout. Please try again."
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")
        return "🔧 System processing error occurred."
