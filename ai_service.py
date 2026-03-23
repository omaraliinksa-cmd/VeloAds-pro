import os
import json
from openai import AsyncOpenAI

class AIService:
    def __init__(self):
        # يسحب المفتاح اللي حطيناه في ملف .env
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_ad_content(self, product_data: dict, platform: str = "TikTok", tone: str = "Energetic") -> dict:
        """توليد سيناريو الإعلان ووصف الفيديو (Prompt)"""
        prompt = f"""
        Analyze this product: {product_data['title']}
        Description: {product_data['description']}
        Target Platform: {platform}
        Tone: {tone}
        
        Tasks:
        1. Write a 15-second catchy ad script in Arabic.
        2. Create a detailed visual prompt for Runway Gen-3 video generator. 
           The prompt should be cinematic, high quality, and focus on the product benefits.
        
        Return the result in JSON format:
        {{
            "script": "...",
            "video_prompt": "..."
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error in OpenAI: {e}")
            return {
                "script": "حدث خطأ في توليد السيناريو",
                "video_prompt": "Cinematic product shot, high resolution"
            }
