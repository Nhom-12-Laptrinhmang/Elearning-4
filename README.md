# BlogAPI — README hoàn chỉnh

Tài liệu này hướng dẫn chi tiết cách thiết lập, chạy, kiểm thử và chuẩn bị project để push/nộp (đặc biệt phù hợp cho nộp nhóm). Nội dung gồm: yêu cầu, cài đặt, biến môi trường, chạy server, cách test bằng curl/Postman, export database, giải thích cơ chế logout/blacklist, và checklist nộp.

---

## Yêu cầu môi trường

- Python 3.8+ (mình đã dùng Python 3.12 trong môi trường dev nhưng project tương thích từ 3.8+)
- pip
- SQLite3 (để export/import DB; không bắt buộc để chạy app vì repo có thể dùng file DB cục bộ)

Khuyến nghị: tạo virtualenv để cô lập phụ thuộc.

---

## Cài đặt nhanh (local)

1) Mở terminal và chuyển tới thư mục project:

```bash
cd /path/to/Ltm-Swagger UI-Project
```

2) Tạo & kích hoạt virtualenv (macOS/Linux zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Cài dependencies:

```bash
pip install -r requirements.txt
```

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

---

## Chạy server

Chạy bằng uvicorn (hot-reload để dev):

```bash
uvicorn app.main:app --reload
```

Sau khi chạy, Swagger UI có sẵn tại:

- http://127.0.0.1:8000/docs (interactive)
- http://127.0.0.1:8000/redoc

Ứng dụng cũng in thông tin khởi động ra terminal (APP_NAME, DB URL, ...).

---

## API chính và ví dụ (curl)

1) Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

2) Login (lấy access token):

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

Response mẫu:

```json
{"status":"success","message":"Logged in","data":{"access_token":"<JWT>","token_type":"bearer"}}
```

3) Dùng token gọi API cần auth (ví dụ tạo blog):

```bash
curl -X POST http://127.0.0.1:8000/api/blog/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  -d '{"title":"My post","content":"Hello"}'
```

4) Logout / Revoke token

- POST `/auth/logout` — protected endpoint, yêu cầu token hợp lệ; sẽ thêm token vào blacklist (token sẽ bị từ chối sau đó).
- POST `/auth/revoke` — cũ (low-level): chấp nhận header Authorization và blacklist token (không cần phụ thuộc `get_current_user`).

Ví dụ:

```bash
curl -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer <JWT>"
```

Sau khi logout/revoke, mọi request sử dụng token đó sẽ bị trả 401 với message "Token has been revoked".

---

## Postman

Mình đã đặt sẵn `postman_collection.json` ở gốc repo (trimmed, dễ đọc). Hướng dẫn:

1) Import file `postman_collection.json` vào Postman (File -> Import).
2) Tạo Environment với biến `baseUrl` (mặc định là `http://127.0.0.1:8000`) và `bearerToken` (mặc định rỗng).
3) Gọi `Auth -> Login`, copy `access_token` từ response và dán vào `{{bearerToken}}` (hoặc mình có thể chèn script auto-set nếu bạn muốn).

Tip: nếu muốn sinh collection tự động từ OpenAPI thì có lệnh:

```bash
# export openapi.json (app đang chạy)
curl -s http://127.0.0.1:8000/openapi.json -o openapi.json

# convert to Postman collection (cần node & npx)
npx openapi-to-postmanv2 -s ./openapi.json -o postman_collection.json
```

---

## Cơ chế blacklist / logout (giải thích kỹ)

- Hiện implementation:
  - Có 1 in-memory blacklist (set) để nhanh chóng blacklist token khi logout.
  - Mình cũng thêm model `TokenBlacklist` (SQLite) và service `app/services/token_blacklist.py` để ghi persistent nếu DB hoạt động.
  - Dependency `get_current_user` (ở `app/utils.py`) kiểm tra blacklist (cả in-memory & DB) trước khi decode token — nên token bị revoke sẽ không được chấp nhận.

- Lưu ý:
  - In-memory blacklist mất khi restart server (khi đó nếu bạn muốn persist thì dùng DB-backed blacklist -> mình đã thêm ghi vào DB khi `db` được truyền vào helper `add_to_blacklist`).
  - Nếu muốn thay thế blacklist theo `jti` (token id) thay vì lưu raw token, mình có thể cập nhật hàm tạo token để thêm `jti` claim và blacklist bằng jti (tốt hơn cho storage và security).

Files liên quan:
- `app/routers/auth.py`: routes `login`, `register`, `revoke`, `logout`.
- `app/services/token_blacklist.py` (mới): helper `add_to_blacklist`, `is_blacklisted`.
- `app/database.py`: thêm model `TokenBlacklist`.
- `app/utils.py`: dependency `get_current_user` đã được cập nhật để check blacklist.

---

## Export / backup database

Nếu bạn muốn export schema / dump có data:

```bash
# chỉ schema (structure)
sqlite3 test.db .schema > schema.sql

# toàn bộ dump (schema + data)
sqlite3 test.db ".dump" > dump_with_data.sql
```

Bạn có thể đặt tên file dump tuỳ thích (ví dụ `dump.sql` hay `data.sql`).

---

## Tests (nếu có)

Project có folder `tests/` sẵn trong repo, bao gồm file `tests/test_main.py` (một bộ test end-to-end nhỏ dùng TestClient). Dưới đây là cách chạy nhanh từ terminal và một số lưu ý để debug.

1) Chạy toàn bộ test bằng pytest (khuyến nghị):

```bash
# chạy tất cả tests
pytest -q

# chạy tests cụ thể (ví dụ file test_main.py)
pytest tests/test_main.py -q

# chạy 1 test function trong file
pytest tests/test_main.py::test_login -q
```

2) Chạy file test trực tiếp (script có `if __name__ == '__main__'`):

```bash
python3 tests/test_main.py
```

Lưu ý: file `tests/test_main.py` đã được viết để chạy theo cả 2 cách. Khi chạy trực tiếp bằng `python`, các hàm sẽ chạy theo thứ tự trong file.

3) Một vài vấn đề thường gặp & cách khắc phục

- Virtualenv / dependencies: luôn đảm bảo đã active `.venv` và đã `pip install -r requirements.txt`.
- Database: tests sử dụng cấu hình DB trong `DATABASE_URL` (mặc định `sqlite:///./test.db`). Nếu chạy test nhiều lần bạn có thể muốn reset DB (xóa `test.db`) hoặc dùng file DB riêng cho test.
- Token / người dùng: tests tạo user `testuser` — nếu user đã tồn tại, route register có thể trả 400; test vẫn tiếp tục (code đã cho phép). Tuy nhiên nếu login thất bại, kiểm tra password/hash hoặc dữ liệu trong DB.
- Endpoints: file test gọi một vài route (ví dụ `/api/blog/all` hoặc `/api/blogs/`); nếu project bạn đã đổi path, test sẽ báo 404. Bạn có thể sửa test hoặc routes để trùng.
- Upload file: test tạo file tạm `tests/test_upload.txt` trước khi upload; đảm bảo thư mục `tests/` có quyền ghi.

4) Debug nhanh khi test fail

- Xem output lỗi pytest (chạy không -q để thấy chi tiết):
  ```bash
  pytest tests/test_main.py -q -vv
  ```
- Chạy test file bằng python để xem print debug (test file có nhiều print):
  ```bash
  python3 tests/test_main.py
  ```
- Kiểm tra logs: khi import `app.main`, ứng dụng in thông tin database và config; kiểm tra terminal để biết DB URL đang dùng.

5) CI / Headless environment

- Nếu chạy trong CI, đảm bảo cài python, pip, pytest và set biến môi trường nếu cần (ví dụ `DATABASE_URL`).

Nếu bạn muốn, mình có thể:
- Viết một test nhỏ bổ sung (pytest) cho flow login->logout->blocked,
- Hoặc điều chỉnh `tests/test_main.py` để phù hợp hoàn toàn với routes hiện tại của bạn (nếu có endpoint khác tên).

---

## Checklist trước khi push / nộp

1. Đảm bảo không commit file `.env` chứa `SECRET_KEY`.
2. Kiểm tra `requirements.txt` đã đầy đủ.
3. Include `postman_collection.json` (trimmed) — file này đã sẵn sàng.
4. Nếu bạn giữ DB mẫu để nộp, include `test.db` hoặc `dump_with_data.sql` — chú ý kích thước.
5. Viết ngắn README (cái này) vào repo root.

---

## Các lệnh hữu ích nhanh (copy/paste)

```bash
# tạo và activate venv
python3 -m venv .venv
source .venv/bin/activate

# cài deps
pip install -r requirements.txt

# chạy server
uvicorn app.main:app --reload

# export schema
sqlite3 test.db .schema > schema.sql

# export dump có data
sqlite3 test.db ".dump" > dump_with_data.sql

# convert OpenAPI -> Postman (cần node/npm)
npx openapi-to-postmanv2 -s http://127.0.0.1:8000/openapi.json -o postman_collection.json
```

---

## Tiếp tục (tùy chọn mình làm giúp)

Nếu bạn muốn mình tiếp tục: mình có thể

- Thêm script auto-set `bearerToken` trong `postman_collection.json` để login tự gán token vào environment.
- Chuyển blacklist sang jti-based design (thay đổi token creation + checks).
- Thêm ví dụ test pytest nhỏ cho logout workflow (login -> logout -> request bị 401).

Chọn 1-2 mục mình làm tiếp cho bạn, hoặc mình sẽ dừng ở đây nếu README đã ok để bạn push.
# Backend Project — Setup & Submission Guide

This README explains how to set up, run, test, and prepare the project for submission. Follow the steps exactly to avoid runtime issues when your instructor runs the code.

## Requirements

## Quick start (recommended)
1. Open a terminal and change to the project folder:

```bash
cd /Users/melaniepham/Downloads/backend-project
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS / Linux (zsh/bash)

# Hướng dẫn ngắn (phiên bản tiếng Việt)

File này hướng dẫn nhanh cách chạy project để nộp: ngắn gọn, đầy đủ bước cơ bản để giảng viên chạy được.

Yêu cầu:
- Python 3.8+

