import sys, os
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
    headers = {"Authorization": f"Bearer {token}"}
    # Thư mục chứa file test
    test_files_dir = "tests/test_files"
    
    # Kiểm tra có ảnh test không
    image_files = [f for f in os.listdir(test_files_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(test_files_dir) else []
    
    if image_files:
        # Nếu có ảnh, dùng ảnh đầu tiên tìm thấy
        test_file_name = image_files[0]
        test_file_path = os.path.join(test_files_dir, test_file_name)
        content_type = "image/jpeg" if test_file_name.lower().endswith(('.jpg', '.jpeg')) else "image/png"
        print(f"📸 Sử dụng file ảnh: {test_file_name}")
    else:
        # Nếu không có ảnh, dùng file text
        test_file_name = "test_upload.txt"
        test_file_path = "tests/test_upload.txt"
        content_type = "text/plain"
        if not os.path.exists(test_file_path):
            print("⚠️ Không tìm thấy file test, tạo file mới...")
            with open(test_file_path, "w") as f:
                f.write("This is a test file for upload testing.")
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
    schema_file = "schema.sql"
    data_file = "all_test_data.sql"
    
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
