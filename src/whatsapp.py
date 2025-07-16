import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("src.whatsapp")

class WhatsAppSender:
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")  
        if not self.token or not self.phone_number_id:
            raise Exception("❌ لازم WHATSAPP_TOKEN و PHONE_NUMBER_ID في .env")

    async def send_text(self, to: str, text: str):
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = httpx.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"❌ Send failed: {response.status_code} - {response.text}")
            raise Exception("❌ فشل إرسال رسالة نصية")
        logger.info("✅ Text sent")

    async def send_voice_note(self, to: str, audio_path: str):
        # ✅ Step 1: Upload OGG (voice note)
        with open(audio_path, "rb") as f:
            upload_resp = httpx.post(
                f"https://graph.facebook.com/v20.0/{self.phone_number_id}/media",
                headers={"Authorization": f"Bearer {self.token}"},
                files={
                    "file": (os.path.basename(audio_path), f, "audio/ogg; codecs=opus")
                },
                data={
                    "messaging_product": "whatsapp",
                    "type": "audio"
                }
            )

        if upload_resp.status_code != 200:
            logger.error(f"❌ Failed to upload audio: {upload_resp.status_code} - {upload_resp.text}")
            raise Exception("❌ فشل رفع ملف الصوت")

        media_id = upload_resp.json().get("id")
        logger.info(f"✅ Audio uploaded, media_id: {media_id}")

        # ✅ Step 2: Send audio (voice note)
        message_payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {
                "id": media_id
            }
        }

        send_resp = httpx.post(
            f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json=message_payload
        )

        if send_resp.status_code != 200:
            logger.error(f"❌ Send audio failed: {send_resp.status_code} - {send_resp.text}")
            raise Exception("❌ فشل إرسال الصوت كـ voice note")

        logger.info("✅ Voice note sent")
