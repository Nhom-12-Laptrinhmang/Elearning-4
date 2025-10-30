from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, blog
from .database import Base, engine
from .config import config   # ✅ import file config của bạn
import os
from pathlib import Path

# ⚙️ Tạo database tables
Base.metadata.create_all(bind=engine)

# 🚀 Khởi tạo ứng dụng FastAPI với tên lấy từ biến môi trường
app = FastAPI(
    title=config.APP_NAME,
    description="REST API Blog project using FastAPI",
    version="1.0.0"
)

# 🌐 Cấu hình CORS (cho phép truy cập từ frontend hoặc Swagger UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ nên giới hạn trong production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Đăng ký router (nhóm các API)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(blog.router, prefix="/api", tags=["Blog"])


@app.on_event("startup")
def ensure_runtime_dirs():
    """Ensure runtime directories and folders exist when the app starts.

    This helps clones run out-of-the-box (uploads folder, and database folder
    if DATABASE_URL points to a file in a subdirectory).
    """
    # ensure uploads/received exists
    uploads_dir = Path("uploads")
    received_dir = uploads_dir / "received"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    received_dir.mkdir(parents=True, exist_ok=True)

    # ensure database folder exists if DATABASE_URL points to a file path
    # e.g. sqlite:///./data/test.db -> create ./data
    if config.DATABASE_URL.startswith("sqlite:///"):
        db_path = config.DATABASE_URL.replace("sqlite:///", "")
        db_dir = Path(db_path).parent
        if str(db_dir) and str(db_dir) != ".":
            db_dir.mkdir(parents=True, exist_ok=True)

# 🧠 In thông tin môi trường khi app khởi động
print("===========================================")
print(f"🚀 Starting {config.APP_NAME} in {config.ENV} mode")
print(f"🔐 Secret key: {config.SECRET_KEY[:5]}... (hidden)")
print(f"📦 Database URL: {config.DATABASE_URL}")
print("📚 Documentation URLs:")
print("   API docs: \033[36mhttp://localhost:8000/docs\033[0m")
print("   Alternative docs: \033[36mhttp://localhost:8000/redoc\033[0m")
print("===========================================")
