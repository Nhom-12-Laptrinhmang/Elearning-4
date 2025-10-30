# BlogAPI — README hoàn chỉnh

Tài liệu này hướng dẫn chi tiết cách thiết lập, chạy, kiểm thử và chuẩn bị project để push . Nội dung gồm: yêu cầu, cài đặt, biến môi trường, chạy server, cách test bằng curl/Postman, export database, giải thích cơ chế logout/blacklist, và checklist nộp.

---

## Yêu cầu môi trường

- Python 3.8+ (mình đã dùng Python 3.12 trong môi trường dev nhưng project tương thích từ 3.8+)
- pip
- SQLite3 (để export/import DB; không bắt buộc để chạy app vì repo có thể dùng file DB cục bộ)

Khuyến nghị: tạo virtualenv để cô lập phụ thuộc.

---

## Cài đặt nhanh (local)

1) Mở terminal và chuyển tới thư mục project (dùng đường dẫn tương đối hoặc đường dẫn nơi bạn clone repository):

```bash
# Thay <project-root> bằng đường dẫn tới thư mục chứa project trên máy của bạn
cd "<project-root>"
# ví dụ: cd "~/projects/Ltm-Swagger-UI-Project" hoặc cd "/home/user/work/Ltm-Swagger-UI-Project"
```

2) Tạo & kích hoạt virtualenv (macOS/Linux zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```
```
# Ghi chú ngắn cho 2 lệnh phía trên:
# - Tạo virtual environment (thư mục .venv) để cô lập phụ thuộc
# - Kích hoạt virtualenv để các lệnh pip/pytest dùng môi trường này

3) Cài dependencies:

```bash
pip install -r requirements.txt
```
```
# Ghi chú: lệnh trên cài toàn bộ thư viện cần cho project từ file requirements.txt

4) Tạo file `.env` ở gốc project (nếu chưa có). Mẫu:

```env
SECRET_KEY=replace-with-your-secret
DATABASE_URL=sqlite:///./test.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# (Không commit .env có secret key lên git!)
```

5) Tạo database (nếu muốn) và khởi tạo tables (app sẽ tự tạo tables khi import `app.main`):

```bash
# (tùy chọn) tạo file sqlite trống
sqlite3 test.db "VACUUM;"

# khởi chạy server (xem bước kế)
```

# Ghi chú: lệnh sqlite3 VACUUM dùng để tạo/tối ưu file SQLite (test.db) nếu cần

---

## Chạy server

Chạy bằng uvicorn (hot-reload để dev):

```bash
uvicorn app.main:app --reload
```

# BlogAPI — Hướng dẫn chạy, kiểm thử và nộp bài (Tiếng Việt)

Tài liệu này mô tả đầy đủ cách cài đặt, chạy, kiểm thử và chuẩn bị project để nộp/submit. Có các lệnh copy/paste để bạn thao tác nhanh.

---

## Mục lục
- Yêu cầu môi trường
- Cài đặt nhanh
- Biến môi trường (mẫu `.env`)
- Chạy server

# BlogAPI — Hướng dẫn chạy, kiểm thử 

Tóm tắt nhanh (TL;DR):
- Clone repo, tạo virtualenv, cài `requirements.txt`, chạy `python run.py` hoặc `uvicorn app.main:app --reload` rồi dùng Swagger ở `/docs`.

---
```bash
uvicorn app.main:app --reload
```

Hoặc dùng script `run.py` nếu bạn muốn:

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
