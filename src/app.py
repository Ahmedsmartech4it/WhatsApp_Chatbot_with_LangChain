import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from src.ai_agent import AIAgent
from src.stt import stt
from src.whatsapp import WhatsAppSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("src.app")

app = FastAPI()
agent = AIAgent()
whatsapp = WhatsAppSender()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.get("/")
async def root():
    return {"message": "🔥 WhatsApp Chatbot Running"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(content=params.get("hub.challenge"), status_code=200)
    return PlainTextResponse(content="Invalid verification token", status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    logger.info(f"Webhook data: {data}")

    try:
        entry = data["entry"][0]["changes"][0]["value"]

        if "messages" in entry:
            message = entry["messages"][0]
            from_number = message["from"]
            mtype = message["type"]

            if mtype == "audio":
                media_id = message["audio"]["id"]
                text = await stt.process(media_id)
                return_audio = True
            elif mtype == "text":
                text = message["text"]["body"]
                return_audio = False
            else:
                logger.info("✅ Ignored message type")
                return {"status": "ignored"}

            logger.info(f"✅ Text processed: {text}")

            response = await agent.generate_response(text, return_audio=return_audio)

            await whatsapp.send_text(from_number, response["text"])
            if response["audio"]:
                await whatsapp.send_voice_note(from_number, response["audio"])

    except Exception as e:
        logger.exception(f"❌ Error handling message: {e}")

    return {"status": "ok"}

