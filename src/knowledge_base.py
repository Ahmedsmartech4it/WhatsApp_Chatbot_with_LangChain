import pandas as pd
from typing import List, Dict
import logging
import os
from difflib import SequenceMatcher
import re
import pandas as pd
import os
logger = logging.getLogger("src.knowledge_base")

class KnowledgeBase:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found at: {path}")
        self.df = pd.read_csv(path, encoding="utf-8-sig").fillna("")
        logger.info(f"✅ تم تحميل قاعدة المعرفة من {path}")
        
        
        self.df['السعر (جنيه مصري)'] = self.df['السعر (جنيه مصري)'].apply(self._convert_price_to_number)
        self.df['الكمية في المخزن'] = self.df['الكمية في المخزن'].apply(self._convert_qty_to_number)

    def search(self, query: str) -> List[Dict]:
        query = query.lower().strip()
        results = []
        
       
        for _, row in self.df.iterrows():
            product = row['اسم المنتج'].lower().strip()
            
        
            if any(word in product for word in query.split()):
                results.append({
                    "اسم_المنتج": row['اسم المنتج'],
                    "السعر": f"{row['السعر (جنيه مصري)']:.2f} جنيه",
                    "الكمية": row['الكمية في المخزن']
                })
        
        
        if not results:
            for _, row in self.df.iterrows():
                product = row['اسم المنتج'].lower().strip()
                similarity = SequenceMatcher(None, query, product).ratio()
                
                if similarity > 0.6: 
                    results.append({
                        "اسم_المنتج": row['اسم المنتج'],
                        "السعر": f"{row['السعر (جنيه مصري)']:.2f} جنيه",
                        "الكمية": row['الكمية في المخزن']
                    })

        if not results:
            logger.warning(f"❌ لا يوجد تطابق مع الاستعلام: {query}")
        return results

    def _convert_price_to_number(self, price_text: str) -> float:
        try:
            
            words = price_text.split()
            total = 0.0
            
         
            if 'جنيهًا' in words or 'جنيه' in words:
                idx = words.index('جنيهًا') if 'جنيهًا' in words else words.index('جنيه')
                num_words = ' '.join(words[:idx])
                total += self._words_to_number(num_words)
            
           
            if 'قرشًا' in words or 'قرش' in words:
                idx = words.index('قرشًا') if 'قرشًا' in words else words.index('قرش')
                num_words = ' '.join(words[idx-1:idx])
                total += self._words_to_number(num_words) / 100
            
            return round(total, 2)
        except:
            return 0.0

    def _convert_qty_to_number(self, qty_text: str) -> int:
        try:
            
            words = qty_text.replace('منتجًا', '').replace('منتجات', '').strip()
            return self._words_to_number(words)
        except:
            return 0

    def _words_to_number(self, text: str) -> int:
        
        word_to_num = {
            'واحد': 1, 'اثنان': 2, 'ثلاثة': 3, 'أربعة': 4, 'خمسة': 5,
            'ستة': 6, 'سبعة': 7, 'ثمانية': 8, 'تسعة': 9, 'عشرة': 10,
            'أحد عشر': 11, 'اثنا عشر': 12, 'ثلاثة عشر': 13, 'أربعة عشر': 14,
            'خمسة عشر': 15, 'ستة عشر': 16, 'سبعة عشر': 17, 'ثمانية عشر': 18,
            'تسعة عشر': 19, 'عشرون': 20, 'ثلاثون': 30, 'أربعون': 40,
            'خمسون': 50, 'ستون': 60, 'سبعون': 70, 'ثمانون': 80,
            'تسعون': 90, 'مائة': 100, 'مئتان': 200, 'ثلاثمائة': 300,
            'أربعمائة': 400, 'خمسمائة': 500, 'ستمائة': 600, 'سبعمائة': 700,
            'ثمانمائة': 800, 'تسعمائة': 900, 'ألف': 1000
        }
        
        parts = text.split(' و')
        total = 0
        for part in parts:
            if part in word_to_num:
                total += word_to_num[part]
        return total

def get_formatted_csv_context(path: str) -> str:
   

    df = pd.read_csv(path, encoding="utf-8-sig").fillna("")
    if df.empty:
        raise ValueError("❌ الملف فاضي")

    products = []
    for _, row in df.iterrows():
        product_info = "، ".join(f"{k}: {v}" for k, v in row.items())
        products.append(f"- {product_info}")
    return "\n".join(products)
