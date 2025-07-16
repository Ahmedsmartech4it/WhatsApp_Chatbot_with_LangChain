import logging
from typing import Dict, Any
from src.knowledge_base import KnowledgeBase, get_formatted_csv_context
from src.tts import TTSProcessor
from src.processor import MessageProcessor

logger = logging.getLogger("src.ai_agent")

class AIAgent:
    def __init__(self):
        self.kb = KnowledgeBase("data/data.csv")
        self.processor = MessageProcessor()
        self.history = []
        logger.info("✅ AI Agent initialized with buffer memory and GPT-4.1")

    async def generate_response(self, query: str, return_audio: bool = False) -> Dict[str, Any]:
        self.history.append({"role": "user", "content": query})

        context = get_formatted_csv_context("data/data.csv")

        messages = [{
            "role": "system",
            "content": f"""
انت شغال كخدمة عملاء لمحل فاكهة وخضار، بتتكلم دايمًا مع الزباين باللهجة المصرية بطريقة ودودة ومريحة. هدفك تجاوب على أسئلة الأسعار، الأنواع المتاحة، العروض، الخصومات، والتوصيل.

لو حد سأل عن نوع معين، شوف في قاعدة البيانات ورد عليه بالسعر والعروض لو فيه، ولو مش متاح قوله إنه مش متاح دلوقتي بشكل مهذب.

أمثلة للردود:
- لو الزبون سأل "عندك موز؟" ممكن ترد: "أيوه عندنا موز بلدي بـ 18 جنيه الكيلو، ومستورد بـ 25 جنيه. كمان عاملين عرض لو خدت 3 كيلو هتدفع تمن 2 ونص بس 🎉 تحب أجيبلك قد ايه؟"
- لو سأل "فيه خصومات؟" ترد: "أيوه فيه عرض النهاردة على الطماطم، كيلو ونص بـ 15 بدل 20، وعرض كمان على التفاح المستورد خد 3 كيلو بـ 100 جنيه بس 🍏"
- لو نوع مش موجود: "خلص من عندنا دلوقتي، بس راجع بكرة وهيكون متوفر بإذن الله، تحب أحجزلك كمية؟"

خليك دايمًا مهذب، واضح، مختصر، ولو السؤال مش واضح اسأل بلطف "ممكن توضحلي أكتر يا فندم؟"

قاعدة البيانات الحالية:
{context}
""".strip()
        }] + self.history


        answer = await self.processor.run(messages)
        self.history.append({"role": "assistant", "content": answer})

        audio = None
        if return_audio:
            tts = TTSProcessor()
            audio = await tts.generate_audio(answer)

        return {"text": answer, "audio": audio}
