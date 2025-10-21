import os
from dotenv import load_dotenv

# ✅ Load toàn bộ biến môi trường từ file .env ở gốc dự án
load_dotenv()

class Config:
    # 🔐 Biến bí mật (JWT key)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")

    # 🗄️ Kết nối database (SQLite hoặc các DB khác)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # ⚙️ Thông số bảo mật token
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # 🌍 Môi trường chạy app (dev/test/prod)
    ENV: str = os.getenv("ENV", "development")

    # 📦 Tên ứng dụng (dùng cho title trong Swagger)
    APP_NAME: str = os.getenv("APP_NAME", "BlogAPI")

# ✅ Tạo instance config toàn cục
config = Config()
