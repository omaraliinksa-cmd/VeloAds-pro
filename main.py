from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import Base, Video
from tasks import create_elite_video_task
from pydantic import BaseModel

# إنشاء الجداول في قاعدة البيانات تلقائياً
Base.metadata.create_all(bind=engine)

app = FastAPI(title="VeloAds Pro Elite")

class AdRequest(BaseModel):
    product_name: str
    style: str = "TikTok Viral"

@app.get("/")
def home():
    return {"message": "VeloAds API is Live & Free!"}

@app.post("/api/create")
def create_ad(request: AdRequest, db: Session = Depends(get_db)):
    # 1. حفظ الطلب في قاعدة البيانات
    new_video = Video(
        product_url=request.product_name, # نستخدمه كإسم للمنتج حالياً
        status="queued",
        progress="جاري البدء..."
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # 2. إرسال المهمة للـ Worker (عبر Celery)
    create_elite_video_task.delay(new_video.id, request.product_name, request.style)

    return {"id": new_video.id, "status": "queued"}

@app.get("/api/status/{ad_id}")
def get_status(ad_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == ad_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return {
        "status": video.status,
        "progress": video.progress,
        "video_url": video.url,
        "script": video.ad_script
    }
