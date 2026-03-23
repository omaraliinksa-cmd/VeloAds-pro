from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.scraper import ScraperService
from app.ai_service import AIService
from app.runway_service import RunwayService
import logging

router = APIRouter()

# نموذج البيانات اللي يرسلها المستخدم (رابط المنتج)
class AdRequest(BaseModel):
    product_url: HttpUrl
    target_platform: str = "TikTok"
    tone: str = "Energetic"

@router.post("/generate")
async def generate_ad(request: AdRequest):
    """
    العملية الكبرى:
    1. كشط بيانات المنتج (Scraper)
    2. توليد السيناريو والوصف (OpenAI)
    3. إرسال الطلب لتوليد الفيديو (Runway)
    """
    try:
        # 1. كشط البيانات
        scraper = ScraperService()
        product_data = await scraper.fetch_product_data(str(request.product_url))
        
        if not product_data:
            raise HTTPException(status_code=400, detail="تعذر استخراج بيانات المنتج من الرابط")

        # 2. توليد السيناريو والوصف البصري عبر الذكاء الاصطناعي
        ai_service = AIService()
        ad_content = await ai_service.generate_ad_content(
            product_data=product_data,
            platform=request.target_platform,
            tone=request.tone
        )

        # 3. إرسال الطلب للمخرج Runway
        runway_service = RunwayService()
        video_task = await runway_service.generate_video(
            prompt=ad_content['video_prompt']
        )

        # النتيجة اللي ترجع للمستخدم على الشاشة
        return {
            "status": "processing",
            "task_id": video_task.get("id"),
            "ad_script": ad_content['script'],
            "product_name": product_data['title'],
            "message": "بدأت عملية توليد الفيديو بنجاح!"
        }

    except Exception as e:
        logging.error(f"Error in ad generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"حدث خطأ داخلي: {str(e)}")
