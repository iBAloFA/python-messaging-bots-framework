# app/whatsapp_main.py
import logging
from fastapi import FastAPI, Request, Response, status
from config import settings
from app.handlers.llm_engine import get_ai_response
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Check settings strings during server load
if settings.whatsapp_api_token == "mock_key":
    logger.warning("🛑 WHATSAPP_API_TOKEN is unconfigured in your environment.")
    logger.info("💡 Webhook engine will still successfully capture, parse, and process mock payloads locally.")

@app.get("/webhook/whatsapp")
async def whatsapp_verification(request: Request):
    """Handles the initial secure verification handshake requested by Meta."""
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.whatsapp_verify_token:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Verification Mismatch", status_code=status.HTTP_403_FORBIDDEN)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook_handler(request: Request):
    """Receives incoming user chat payloads safely."""
    try:
        payload = await request.json()
        logger.info(f"Received Webhook Payload: {payload}")
        
        if "entry" in payload and payload["entry"][0]["changes"][0]["value"].get("messages"):
            message_data = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            from_phone_number = message_data["from"]
            
            if message_data.get("type") == "text":
                user_text = message_data["text"]["body"]
                logger.info(f"Extracted User Text: {user_text}")
                
                # Process data through the unified platform-agnostic AI core
                ai_reply = await get_ai_response(f"wa_{from_phone_number}", user_text)
                logger.info(f"AI Core Generated Reply: {ai_reply}")
                
                # Attemp outbound delivery routing safely
                await send_whatsapp_message(from_phone_number, ai_reply)
                
        return {"status": "success"}
    except Exception as e:
        logger.error(f"WhatsApp Pipeline Failure Traceback: {e}")
        return Response(content="Internal Processing Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def send_whatsapp_message(to_phone: str, text: str):
    """Dispatches outbound response payloads back to Meta servers."""
    if settings.whatsapp_api_token == "mock_key":
        logger.info(f"📤 [MOCK OUTBOUND] Route wa_{to_phone} -> Text: {text}")
        return

    url = f"https://facebook.com{settings.phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text}
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=5.0)
            logger.info(f"Meta Graph Outbound Live Delivery Status: {response.status_code}")
    except Exception as e:
        logger.warning(f"Outbound network dispatch failed cleanly: {e}")
