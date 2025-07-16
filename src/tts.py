# src/tts.py
import os
import httpx
import logging
import uuid
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("src.tts")


class TTSProcessor:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")  # Haytham voice
        if not self.api_key:
            raise Exception("❌ لم يتم العثور على ELEVEN_API_KEY في .env")

    async def generate_audio(self, text: str) -> str:
        logger.info(f"TTS generating: {text}")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.3,
                "similarity_boost": 0.3
            }
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"❌ ElevenLabs TTS Error: {response.status_code} - {response.text}")
            raise Exception("❌ فشل توليد الصوت من ElevenLabs")

        unique_filename = f"data/audio/{uuid.uuid4().hex}"
        mp3_path = f"{unique_filename}.mp3"
        ogg_path = f"{unique_filename}.ogg"

        with open(mp3_path, "wb") as f:
            f.write(response.content)

        AudioSegment.from_mp3(mp3_path).export(ogg_path, format="ogg", codec="libopus")
        logger.info(f"✅ Converted to ogg: {ogg_path}")

        return ogg_path
