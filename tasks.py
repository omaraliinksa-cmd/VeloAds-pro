import os
import json
import google.generativeai as genai
from celery import Celery
from app.database import SessionLocal
from app.models import Video

# ربط مفتاح جمناي اللي حطيته في الـ .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery('tasks', broker=CELERY_BROKER_URL)

@celery.task
def create_elite_video_task(video_id, product_name, style):
    db = SessionLocal()
    video_entry = db.query(Video).filter(Video.id == video_id).first()
    
    try:
        video_entry.progress = "جاري كتابة السيناريو عبر Gemini AI..."
        db.commit()
        
        # طلب السيناريو الاحترافي
        prompt = f"اكتب سيناريو إعلان فيديو {style} لمنتج {product_name}. النتيجة يجب أن تكون JSON فقط يحتوي على: hook (جملة انطلاقة), scenes (قائمة مشاهد), cta (طلب شراء)."
        response = model.generate_content(prompt)
        
        # تنظيف النص المستلم وتحويله لـ JSON
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        script = json.loads(clean_json)
        
        video_entry.ad_script = json.dumps(script)
        video_entry.progress = "جاري تحضير العرض البصري..."
        db.commit()

        # هنا نستخدم صورة مولدة مجانية كمرحلة أولى (Prototype)
        # الرابط المولد يعتمد على الـ Hook اللي كتبه الذكاء الاصطناعي
        visual_url = f"https://pollinations.ai/p/{script['hook'].replace(' ', '_')}?width=1080&height=1920"

        video_entry.url = visual_url
        video_entry.status = "completed"
        video_entry.progress = "100% - الإعلان جاهز للعرض!"
        db.commit()

    except Exception as e:
        video_entry.status = "failed"
        video_entry.progress = f"Error: {str(e)}"
        db.commit()
    finally:
        db.close()
