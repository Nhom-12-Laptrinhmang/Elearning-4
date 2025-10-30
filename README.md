# BlogAPI — README

Tài liệu này hướng dẫn chi tiết cách thiết lập và chạy project trên Windows, macOS và Linux. Nội dung bao gồm: yêu cầu hệ thống, cài đặt theo từng hệ điều hành, cấu hình và chạy server.

---

## Yêu cầu hệ thống

- Python 3.8+ (đã test trên Python 3.8 đến 3.12)
- pip (trình quản lý gói Python)
- SQLite3 (được cài sẵn trên macOS/Linux, Windows cần cài thêm)

---

## Cài đặt theo hệ điều hành

### Windows

1. Cài đặt Python và pip:
   - Tải Python từ [python.org](https://www.python.org/downloads/windows/)
   - Khi cài đặt, **nhớ tích vào "Add Python to PATH"**
   - Mở Command Prompt để kiểm tra:
     ```cmd
     python --version
     pip --version
     ```

2. Tạo và kích hoạt môi trường ảo:
   ```cmd
   cd đường-dẫn-tới-thư-mục-project
   python -m venv venv
   venv\Scripts\activate
   ```

3. Cài đặt dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

### macOS

1. Cài Python (nếu chưa có):
   ```bash
   # Dùng Homebrew
   brew install python
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```bash
   cd đường-dẫn-tới-thư-mục-project
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 
---

## Bảng lệnh nhanh (Quick commands)

Đây là bảng các lệnh thường dùng, tách theo Windows và macOS/Linux để copy-paste nhanh.

| Hành động | Windows (Command Prompt / PowerShell) | macOS / Linux (bash/zsh) |
|---|---:|---:|
| Tạo virtualenv | `python -m venv venv` | `python3 -m venv venv` |
| Kích hoạt virtualenv | `venv\\Scripts\\activate` | `source venv/bin/activate` |
| Cài dependencies | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Chạy (entrypoint) | `python run.py` | `python3 run.py` |
| Chạy với uvicorn (dev) | `uvicorn app.main:app --reload` | `uvicorn app.main:app --reload` |
| Chạy test | `pytest -q` | `pytest -q` |
| Export DB (dump) | `sqlite3 test.db ".dump" > database/all_test_data.sql` | `sqlite3 test.db ".dump" > database/all_test_data.sql` |
| Zip project (loại trừ venv) | PowerShell: `Compress-Archive -Path * -DestinationPath project.zip -Force -Exclude venv\\*` | `zip -r project.zip . -x "venv/*" ".venv/*" ".DS_Store"` |

Gợi ý khi zip để gửi sang Windows/macOS:
- Loại trừ thư mục `venv` hoặc `.venv` để tránh upload dependency nặng.
- Loại bỏ file hệ thống như `.DS_Store` (macOS) trước khi zip: `find . -name '.DS_Store' -delete`.
- Trên Windows, dùng PowerShell `Compress-Archive` hoặc 7-Zip để giải nén ổn định.

---

## Cấu trúc dự án (Project tree)

Dưới đây là cấu trúc thư mục chính (phiên bản rút gọn). Mô tả nhanh mục đích từng phần.

```text
openapi.json                 # OpenAPI spec (generated)
README.md                    # Hướng dẫn (this file)
requirements.txt             # Python dependencies
run.py                       # Entrypoint script để chạy app (cross-platform)

app/                         # Source code chính (FastAPI app)
   config.py                  # Cấu hình ứng dụng
   database.py                # Kết nối DB / helper
   main.py                    # ASGI app (uvicorn) / routes mount
   models.py                  # ORM / models
   response.py                # helpers response
   schemas.py                 # Pydantic schemas
   utils.py                   # tiện ích chung
   routers/
      auth.py                  # routes auth (login/register/logout)
      blog.py                  # routes blog
   services/
      auth_service.py          # logic auth (create user, verify)
      blog_service.py          # logic blog
      token_blacklist.py       # blacklist / revoke token

database/                    # database helpers and SQL dumps
   all_test_data.sql           # (auto-generated) dump test DB
   seed.py                     # seed scripts

postman/                     # Postman collection(s)
   postman.json

tests/                       # Test suite (pytest)
   conftest.py
   test_main.py

uploads/                     # uploaded files (runtime)
   received/

```

Ghi chú:
- Nếu bạn gửi project cho người dùng Windows, tốt nhất là xóa `venv/` và `.DS_Store`, sau đó zip toàn bộ thư mục project.
- Để giữ file quyền thực thi trên macOS/Linux (nếu có script), người nhận Windows sẽ không cần quyền này — chỉ cần dùng Python để chạy.


### Linux (Ubuntu/Debian)

1. Cài Python và pip (nếu chưa có):
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```bash
   cd đường-dẫn-tới-thư-mục-project
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```
## Cấu hình và chạy server

### 1. Tạo file môi trường

Tạo file `.env` trong thư mục gốc của project với nội dung sau:

```env
SECRET_KEY=replace-with-your-secret
DATABASE_URL=sqlite:///./test.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Khởi chạy server

Có 2 cách để chạy server, chọn 1 trong 2:

#### Cách 1: Dùng script run.py (Đề xuất cho người mới)

**Windows:**
```cmd
python run.py
```

**macOS/Linux:**
```bash
python3 run.py
```

#### Cách 2: Dùng uvicorn trực tiếp (Cho người dùng nâng cao)

**Windows:**
```cmd
uvicorn app.main:app --reload
```

**macOS/Linux:**
```bash
uvicorn app.main:app --reload
```

### 3. Truy cập API

Sau khi chạy thành công:
- API docs: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

## Xử lý lỗi thường gặp

### Windows
1. Lỗi "python không được nhận dạng":
   - Kiểm tra đã tích "Add Python to PATH" khi cài đặt
   - Thử dùng `py` thay vì `python`

2. Lỗi permission khi tạo venv:
   - Chạy Command Prompt với quyền Administrator

### macOS/Linux
1. Lỗi permission:
   ```bash
   sudo chown -R $USER venv/
   ```

2. Lỗi không tìm thấy python3:
   - macOS: `brew install python`
   - Ubuntu: `sudo apt install python3`

### Chung
1. Lỗi "Module not found":
   - Kiểm tra đã activate môi trường ảo chưa
   - Chạy lại `pip install -r requirements.txt`

2. Lỗi port 8000 đã được sử dụng:
   - Thêm `--port 8001` vào lệnh uvicorn
   - Hoặc tìm và tắt process đang dùng port 8000

```bash
python run.py
```

# Ghi chú: dùng `python run.py` nếu bạn muốn 1 entrypoint cố định (cấu hình, logging...)

Docs:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Lưu ý về `run.py` vs `uvicorn`:
- `uvicorn app.main:app --reload` chạy trực tiếp ASGI app với hot-reload (tốt cho development).
- `python run.py` có thể cài sẵn cấu hình khởi động (port, logging, hoặc các thao tác init trước khi run). Dùng phương pháp nào cũng được; README/Makefile scripts sẽ dùng `python run.py` khi cần một entrypoint cố định cho mọi người.

---

## API chính — ví dụ curl

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```
```
# Ghi chú: đăng ký user mới (thay alice/secret bằng thông tin mong muốn)

Login (lấy token):

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```
```
# Ghi chú: đăng nhập, server trả access token (JWT) trong response

Gọi endpoint có auth:

```bash
curl -X POST http://127.0.0.1:8000/api/blog/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  -d '{"title":"My post","content":"Hello"}'
```
```
# Ghi chú: tạo bài blog mới, thay <JWT> bằng token nhận được từ /auth/login

Logout / revoke token:

```bash
curl -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer <JWT>"
```
```
# Ghi chú: logout/revoke token — token sẽ bị blacklist và không thể dùng tiếp

Sau khi logout, token đó sẽ bị blacklist và không thể dùng tiếp.

---

## Postman

File collection nằm trong `postman/postman.json` (compact). Import file này vào Postman để dùng.

Regenerate từ OpenAPI (tuỳ chọn):

```bash
curl -s http://127.0.0.1:8000/openapi.json -o openapi.json
npx openapi2postmanv2 -s ./openapi.json -o postman/postman.json -f
```
```
# Ghi chú:
# - curl: lấy OpenAPI spec từ server đang chạy và lưu thành openapi.json
# - npx openapi2postmanv2: convert OpenAPI -> Postman collection (cần Node/npm)

Lưu ý: lệnh trên cần Node/npm; sẽ ghi đè file collection hiện tại.

---

## Chạy collection tự động (Newman)

```bash
npm i -g newman
newman run postman/postman.json --env-var "baseUrl=http://127.0.0.1:8000" -r html,cli --reporter-html-export newman-report.html
```
```
# Ghi chú:
# - npm i -g newman: cài newman (CLI runner cho Postman)
# - newman run ...: chạy collection và xuất báo cáo HTML

---

## Tests (pytest)

Chạy toàn bộ test:

```bash
pytest -q
```
```
# Ghi chú: chạy tất cả pytest ( -q chạy ở chế độ ngắn gọn )

Chạy file cụ thể:

```bash
pytest tests/test_main.py -q
```

Một vài lưu ý:
- Tests đã được viết để tự tạo user & token khi cần, và export DB vào `database/all_test_data.sql` sau khi chạy.
- Nếu muốn test chạy từ đầu sạch: xóa `test.db` trước khi chạy tests.

---

Chi tiết: cách `all_test_data.sql` được tạo

Trong repository, test suite có một bước (pytest session hook) để xuất (dump) database SQLite test thành file SQL mẫu `database/all_test_data.sql` sau khi tests chạy. Mục đích: cung cấp một dump có schema + dữ liệu mẫu để người khác có thể import hoặc kiểm tra.

Nếu bạn muốn tạo dump này thủ công (không chạy tests), chạy lệnh sau từ thư mục project root:

```bash
# tạo dump schema + data từ test.db
sqlite3 test.db ".dump" > database/all_test_data.sql
```
```
# Ghi chú: lệnh trên xuất toàn bộ DB (schema + data) sang file SQL có thể import lại

Ghi chú:
- Nếu test suite được chạy trong môi trường CI, hook sẽ tự động cập nhật `database/all_test_data.sql` (nếu bạn giữ quyền ghi). Nếu bạn thấy file không được cập nhật, kiểm tra quyền ghi vào thư mục `database/` và đảm bảo `test.db` tồn tại.
- Xóa `test.db` trước khi chạy tests nếu bạn muốn một run hoàn toàn sạch.

---

## Export / backup database

Export schema:

```bash
sqlite3 test.db .schema > database/schema.sql
```

Export dump (schema + data):

```bash
sqlite3 test.db ".dump" > database/all_test_data.sql
```
---

## Lỗi thường gặp & cách khắc phục nhanh

- Thiếu package: `pip install -r requirements.txt` và đảm bảo virtualenv active.
- SQLite locked: xóa `test.db` nếu chấp nhận mất dữ liệu test.
- 404 khi gọi endpoint: kiểm tra route trong `app/routers` và sửa test/collection tương ứng.

---
