# app/whatsapp_main.py
import logging
from fastapi import FastAPI, Request, Response, status
from config import settings
from app.handlers.llm_engine import get_ai_response
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

if settings.whatsapp_api_token == "mock_key":
    logger.warning("⚠️ WHATSAPP_API_TOKEN is unconfigured. Operating in mock data validation mode.")

@app.get("/webhook/whatsapp")
async def whatsapp_verification(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.whatsapp_verify_token:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Verification Mismatch", status_code=status.HTTP_403_FORBIDDEN)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook_handler(request: Request):
    try:
        payload = await request.json()
        logger.info(f"Received JSON Webhook Payload: {payload}")
        
        if "entry" in payload and payload["entry"][0]["changes"][0]["value"].get("messages"):
            message_data = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            from_phone_number = message_data["from"]
            
            if message_data.get("type") == "text":
                user_text = message_data["text"]["body"]
                logger.info(f"Parsed Sender Phone ID: {from_phone_number} | Text: {user_text}")
                
                ai_reply = await get_ai_response(f"wa_{from_phone_number}", user_text)
                logger.info(f"Computed Reply Matrix: {ai_reply}")
                
                await send_whatsapp_message(from_phone_number, ai_reply)
                
        return {"status": "success"}
    except Exception as e:
        logger.error(f"WhatsApp Webhook Processing Exception: {e}")
        return Response(content="Internal Processing Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def send_whatsapp_message(to_phone: str, text: str):
    if settings.whatsapp_api_token == "mock_key":
        logger.info(f"📤 [MOCK OUTBOUND DISPATCH] Target: wa_{to_phone} -> Reply: {text}")
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
            logger.info(f"Meta Graph Server Response Code: {response.status_code}")
    except Exception as e:
        logger.warning(f"Outbound link dropped cleanly: {e}")
