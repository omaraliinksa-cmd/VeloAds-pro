import httpx
from bs4 import BeautifulSoup
import logging

class ScraperService:
    def __init__(self):
        # المتصفح اللي بنستخدمه عشان المواقع ما تشك فينا
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    async def fetch_product_data(self, url: str) -> dict:
        """سحب العنوان والوصف من رابط المنتج"""
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                response = await client.get(url, timeout=15.0)
                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # استخراج اسم المنتج (نبحث في العناوين الرئيسية)
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "منتج جديد"
                
                # استخراج الوصف من وسوم Meta (أفضل طريقة لمعظم المتاجر)
                description = ""
                meta_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    description = meta_desc.get("content", "")

                return {
                    "title": title,
                    "description": description[:500], # نأخذ أول 500 حرف عشان ما نطول على GPT
                    "url": url
                }
            except Exception as e:
                logging.error(f"خطأ في كشط البيانات: {e}")
                return None
