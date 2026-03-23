from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import Base, Video
# لاحظ هنا استدعينا الدالة مباشرة بدون .delay
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
    # 1. حفظ الطلب في قاعدة البيانات بشكل مبدئي
    new_video = Video(
        product_url=request.product_name,
        status="processing",
        progress="جاري التحليل..."
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    # 2. التشغيل المباشر (Direct Execution)
    # هنا السيرفر بينتظر لين يخلص جمناي ويرد عليه بالسيناريو
    try:
        ad_result = create_elite_video_task(new_video.id, request.product_name, request.style)
        return {
            "status": "success",
            "ad_script": ad_result.get("ad_script"),
            "id": new_video.id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
