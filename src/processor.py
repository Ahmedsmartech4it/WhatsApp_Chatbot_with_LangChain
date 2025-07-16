import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("src.processor")

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

class MessageProcessor:
    async def run(self, messages: list) -> str:
        try:
            response = client.chat.completions.create(
                model="openai/gpt-4.1",
                messages=messages,
                temperature=0.3,
                max_tokens=300,
                top_p=0.8
            )
            result = response.choices[0].message.content.strip()
            logger.info(f"✅ LLM Response: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Processor error: {e}")
            return "⚠️ حصل خطأ أثناء المعالجة"
