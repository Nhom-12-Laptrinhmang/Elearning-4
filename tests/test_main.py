import sys, os
import random
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from run import app
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)
test_number = datetime.now().strftime("%H%M")

def test_register():
    global test_username, test_password
    test_username = f"user{test_number}"
    test_password = f"pass{test_number}"
    response = client.post("/auth/register", json={"username": test_username, "password": test_password})
    assert response.status_code in [200, 201, 400]
    print("✅ test_register:", response.json())
    return test_username, test_password

def test_login():
    global token, test_username, test_password
    test_username, test_password = test_register()
    response = client.post("/auth/login", json={"username": test_username, "password": test_password})
    assert response.status_code == 200, f"Lỗi login: {response.text}"
    token = response.json()["data"]["access_token"]
    print("✅ test_login:", {"username": test_username, "password": test_password, "token": token[:25] + "..."})
    return token

def test_create_blog():
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": f"Blog #{test_number}", "content": f"Test content by {test_username}"}
    response = client.post("/api/blog/create", json=data, headers=headers)
    assert response.status_code in [200, 201]
    print("✅ test_create_blog:", response.json())

def test_view_blog():
    response = client.get("/api/blogs/")
    print("🧩 test_view_blog status:", response.status_code)
    print("🧩 test_view_blog response:", response.text)
    assert response.status_code == 200
    print("✅ test_view_blog:", response.json())

def test_search_blog():
    response = client.get("/api/blog/search?q=Blog")
    assert response.status_code == 200
    print("✅ test_search_blog:", response.json())

def test_upload_file():
    # Ensure token is available so this test can run standalone.
    # If token is not defined (running this test alone), perform login which will
    # register+login and set the global `token` used by other tests.
    try:
        _ = token
    except NameError:
        test_login()
    headers = {"Authorization": f"Bearer {token}"}
    # Prefer images from the project's `uploads/` folder (root), fallback to `tests/test_files`
    repo_root = os.path.dirname(os.path.dirname(__file__))
    uploads_dir = os.path.join(repo_root, "uploads")
    test_files_dir = os.path.join(os.path.dirname(__file__), "test_files")

    # Kiểm tra có ảnh test không (ưu tiên uploads/ của project)
    image_files = []
    image_source_dir = None
    if os.path.exists(uploads_dir):
        image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if image_files:
            image_source_dir = uploads_dir

    if not image_files and os.path.exists(test_files_dir):
        image_files = [f for f in os.listdir(test_files_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if image_files:
            image_source_dir = test_files_dir
    
    if image_files:
        # Nếu có ảnh, chọn luân phiên (round-robin) giữa các file để tránh lặp liên tiếp
        # Sắp xếp danh sách để thứ tự ổn định, sau đó dùng file index lưu ở tests/last_upload_index.txt
        image_files.sort()
        index_file = os.path.join(os.path.dirname(__file__), "last_upload_index.txt")
        try:
            if os.path.exists(index_file):
                with open(index_file, "r") as idxf:
                    idx = int(idxf.read().strip() or 0)
            else:
                idx = 0
        except Exception:
            idx = 0

        idx = idx % len(image_files)
        test_file_name = image_files[idx]
        # cập nhật index cho lần chạy kế tiếp
        try:
            with open(index_file, "w") as idxf:
                idxf.write(str((idx + 1) % len(image_files)))
        except Exception:
            pass
        test_file_path = os.path.join(image_source_dir, test_file_name)
        content_type = "image/jpeg" if test_file_name.lower().endswith(('.jpg', '.jpeg')) else "image/png"
        print(f"📸 Sử dụng file ảnh: {test_file_name} từ {os.path.relpath(image_source_dir, repo_root)}")
    else:
        # Nếu không có ảnh, tạo một ảnh PNG placeholder trong thư mục tests/test_files
        test_files_dir_abs = os.path.join(os.path.dirname(__file__), "test_files")
        os.makedirs(test_files_dir_abs, exist_ok=True)
        test_file_name = "test_upload.png"
        test_file_path = os.path.join(test_files_dir_abs, test_file_name)
        content_type = "image/png"
        # 1x1 PNG pixel (base64) — tạo file nếu chưa tồn tại
        if not os.path.exists(test_file_path):
            print("⚠️ Không tìm thấy file ảnh test, tạo ảnh placeholder PNG...")
            import base64
            img_b64 = (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA" 
                "AAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
            )
            with open(test_file_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
    with open(test_file_path, "rb") as f:
        response = client.post("/api/blog/upload", 
            files={"file": (test_file_name, f, content_type)}, 
            headers=headers)
    assert response.status_code in [200, 201]
    print("✅ test_upload_file:", response.json())

def test_logout():
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code in [200, 204]
    print("✅ test_logout:", response.json())

def test_revoke():
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/revoke", headers=headers)
    assert response.status_code in [200, 204]
    print("✅ test_revoke:", response.json())

def test_access_after_revoke():
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/blog/all", headers=headers)
    assert response.status_code in [401, 403]
    print("✅ test_access_after_revoke: token bị chặn sau revoke (đúng)")

def export_to_sql():
    """Export database to SQL file"""
    schema_file = "database/schema.sql"
    data_file = "database/all_test_data.sql"

    with open(data_file, "w") as f:
        f.write(f"-- Data từ lần test lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("-- Bắt đầu transaction\n")
        f.write("BEGIN TRANSACTION;\n\n")

        # Blogs
        f.write("-- Blogs\n")
        os.system('sqlite3 test.db ".mode insert" "SELECT * FROM blogs;" > temp.sql')
        with open("temp.sql", "r") as temp:
            content = temp.read()
            content = content.replace('INSERT INTO "table"', 'INSERT INTO blogs')
            f.write(content + "\n")

        # Users
        f.write("-- Users\n")
        os.system('sqlite3 test.db ".mode insert" "SELECT * FROM users;" > temp.sql')
        with open("temp.sql", "r") as temp:
            content = temp.read()
            content = content.replace('INSERT INTO "table"', 'INSERT INTO users')
            f.write(content + "\n")

        # Token blacklist
        f.write("-- Token blacklist\n")
        os.system('sqlite3 test.db ".mode insert" "SELECT * FROM token_blacklist;" > temp.sql')
        with open("temp.sql", "r") as temp:
            content = temp.read()
            content = content.replace('INSERT INTO "table"', 'INSERT INTO token_blacklist')
            f.write(content + "\n")

        f.write("COMMIT;\n\n")
        f.write("-- End of data\n")

    # Xóa file tạm
    if os.path.exists("temp.sql"):
        os.remove("temp.sql")

    print(f"\n📝 Dữ liệu test đã được lưu vào:")
    print(f"   1. Cấu trúc DB: {schema_file}")
    print(f"   2. Dữ liệu test: {data_file}")
    print(f"\n💡 Để tạo DB test mới:")
    print(f"   sqlite3 new.db < {schema_file}")
    print(f"   sqlite3 new.db < {data_file}")

if __name__ == "__main__":
    print("\n🚀 BẮT ĐẦU CHẠY TEST THỦ CÔNG...\n")
    test_register()
    test_login()
    test_create_blog()
    test_view_blog()
    test_search_blog()
    test_upload_file()
    test_logout()
    test_revoke()
    test_access_after_revoke()
    print("\n🎉 TẤT CẢ TEST ĐÃ HOÀN THÀNH THÀNH CÔNG!")
    export_to_sql()
