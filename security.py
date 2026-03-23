import os
import time
from typing import Dict
import jwt
from passlib.context import CryptContext

# إعدادات التشفير (تنسحب من ملف .env اللي سويناه)
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret_7788")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")

# أداة لتشفير ومقارنة كلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: str) -> Dict[str, str]:
    """إنشاء رمز دخول (Token) للمستخدم لمدة ساعة"""
    payload = {
        "user_id": user_id,
        "expires": time.time() + 3600  # ساعة واحدة
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "access_token": token
    }

def verify_password(plain_password, hashed_password):
    """التحقق هل كلمة المرور صحيحة؟"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """تحويل كلمة المرور لنص مشفر (للحماية)"""
    return pwd_context.hash(password)

def decode_jwt(token: str) -> dict:
    """فك تشفير الرمز للتأكد من هوية المستخدم"""
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return None
