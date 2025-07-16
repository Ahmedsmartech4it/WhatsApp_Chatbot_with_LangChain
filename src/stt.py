import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("src.stt")


class SpeechToText:
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        if not self.token:
            raise Exception("❌ لم يتم العثور على WHATSAPP_TOKEN في .env")

    async def process(self, media_id: str) -> str:
        logger.info(f"🎤 بدء معالجة الصوت media_id: {media_id}")

        meta_resp = httpx.get(
            f"https://graph.facebook.com/v19.0/{media_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        resp_json = meta_resp.json()
        if "url" not in resp_json:
            logger.error(f"❌ WhatsApp API Error in media fetch: {resp_json}")
            raise Exception("❌ فشل تحميل رابط الصوت من واتساب")

        media_url = resp_json["url"]
        logger.info(f"✅ media_url fetched: {media_url}")

        audio_resp = httpx.get(
            media_url,
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if audio_resp.status_code != 200:
            logger.error(f"❌ Error downloading audio file: {audio_resp.status_code}")
            raise Exception("❌ فشل تحميل ملف الصوت")

        files = {"file": ("audio.ogg", audio_resp.content, "audio/ogg")}
        stt_resp = httpx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
            files=files,
            data={"model": "whisper-large-v3-turbo"}
        )

        stt_json = stt_resp.json()
        if "text" not in stt_json:
            logger.error(f"❌ Groq STT error: {stt_json}")
            raise Exception("❌ فشل تحويل الصوت لنص")

        text = stt_json["text"]
        logger.info(f"✅ STT تم تحويل الصوت إلى نص: {text}")
        return text


stt = SpeechToText()
