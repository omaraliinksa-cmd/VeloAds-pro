import os
import httpx
import logging

class RunwayService:
    def __init__(self):
        # يسحب المفتاح السري لـ Runway من ملف .env
        self.api_key = os.getenv("RUNWAYML_API_KEY")
        self.base_url = "https://api.runwayml.com/v1/tasks"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }

    async def generate_video(self, prompt: str):
        """إرسال طلب توليد فيديو إلى Runway Gen-3"""
        payload = {
            "taskType": "text_to_video",
            "model": "gen3a_turbo",
            "promptText": prompt,
            "aspectRatio": "vertical" # مناسب جداً لـ TikTok و Reels
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers,
                    timeout=25.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logging.error(f"خطأ في التواصل مع Runway: {e}")
                return {"id": "error", "status": "failed"}

    async def check_video_status(self, task_id: str):
        """التحقق من حالة الفيديو (هل خلص ولا لسه؟)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{task_id}",
                headers=self.headers
            )
            return response.json()
