import os
import json
import google.generativeai as genai
from database import SessionLocal
from models import Video

# إعداد جمناي مباشرة
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# حذفنا كل ما يخص Celery و Redis عشان يشتغل السيرفر لحاله
def create_elite_video_task(video_id, product_name, style):
    db = SessionLocal()
    video_entry = db.query(Video).filter(Video.id == video_id).first()
    
    try:
        video_entry.progress = "جاري كتابة السيناريو عبر Gemini AI..."
        db.commit()
        
        # طلب السيناريو من ذكاء جوجل
        prompt = f"اكتب سيناريو إعلان فيديو {style} لمنتج {product_name}. النتيجة يجب أن تكون JSON فقط يحتوي على: hook (جملة انطلاقة), scenes (قائمة مشاهد), cta (طلب شراء)."
        response = model.generate_content(prompt)
        
        # تنظيف الرد وتحويله لـ JSON
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        script = json.loads(clean_json)
        
        # حفظ النتائج في قاعدة البيانات
        video_entry.ad_script = json.dumps(script)
        video_entry.progress = "جاري تحضير العرض البصري..."
        db.commit()

        # توليد رابط صورة تجريبية بناءً على الـ Hook
        visual_url = f"https://pollinations.ai/p/{script.get('hook', 'product').replace(' ', '_')}?width=1080&height=1920"

        video_entry.url = visual_url
        video_entry.status = "completed"
        video_entry.progress = "100% - الإعلان جاهز للعرض!"
        db.commit()
        
        # نرجع النتيجة عشان main.
