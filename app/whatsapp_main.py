# app/whatsapp_main.py
import logging
import os
import httpx
from fastapi import FastAPI, Request, Response, status
from app.handlers.llm_engine import get_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_token_123")
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")

@app.get("/webhook/whatsapp")
async def whatsapp_verification(request: Request):
    """Handles the initial secure verification handshake requested by Meta's servers."""
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == WHATSAPP_VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Verification Mismatch", status_code=status.HTTP_403_FORBIDDEN)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook_handler(request: Request):
    """Receives user chat payloads dynamically forwarded from Meta's API clusters."""
    try:
        payload = await request.json()
        
        # Verify JSON properties match standard incoming text message structure
        if "entry" in payload and payload["entry"][0]["changes"][0]["value"].get("messages"):
            message_data = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            from_phone_number = message_data["from"] # Acts as tracking key user_id
            
            if message_data.get("type") == "text":
                user_text = message_data["text"]["body"]
                
                # Run the text payload through your unified AI controller
                ai_reply = await get_ai_response(f"wa_{from_phone_number}", user_text)
                
                # Fire the outbound API delivery request to WhatsApp
                await send_whatsapp_message(from_phone_number, ai_reply)
                
        return {"status": "success"}
    except Exception as e:
        logger.error(f"WhatsApp Pipeline Failure: {e}")
        return Response(content="Internal Processing Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def send_whatsapp_message(to_phone: str, text: str):
    """Sends an outgoing message using Meta's standard Graph API endpoints."""
    url = f"https://facebook.com{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/semibold+json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        logger.info(f"Meta Graph Outbound Delivery Status: {response.status_code}")
