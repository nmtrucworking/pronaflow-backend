# 1. Core Technology Stack

| Thành phần     | Công nghệ            | Lý do lựa chọn                                                                    |
| -------------- | -------------------- | --------------------------------------------------------------------------------- |
| **Framework**  | #FastAPI             | Hiệu năng xử lý bất đồng bộ (Async I/O) vượt trội, tự động sinh tài liệu OpenAPI. |
| **Language**   | #Python v3.10+       | Tận dụng cú pháp hiện đại và Type Hints để đảm bảo chất lượng mã nguồn.           |
| **Validation** | #Pydantic v2         | Kiểm tra dữ liệu đầu vào/đầu ra nghiêm ngặt, đảm bảo Data Integrity.              |
| **Server**     | #Uvicorn / #Gunicorn | ASGI Server đạt chuẩn sản xuất (Production-grade).                                |


# 2. Chiến lược Dữ liệu (Data Persistence Strategy)
## 2.1. Primary Database: PostgreSQL
- **Vai trò:** Lưu trữ dữ liệu quan hệ (Relational Data) và phi cấu trúc (JSON Documents).
- **Quyền truy cập:** Main Backend nắm giữ quyền **Đọc/Ghi (Read/Write)** độc quyền đối với CSDL này.
- **Mô hình ORM:** Sử dụng **SQLAlchemy (Async)** để tương tác với CSDL thông qua các Class Python, giúp code dễ bảo trì và tránh lỗ hổng SQL Injection.
## 2.2. Caching & Messaging: Redis
- **Caching:** Lưu trữ tạm thời các dữ liệu truy cập thường xuyên (Session, User Profile) để giảm tải cho PostgreSQL.
- **Message Broker:** Đóng vai trò hàng đợi (Task Queue) để gửi các tác vụ nặng sang AI Service hoặc Worker Process (gửi email, xử lý file).
# 3. Bảo mật & Định danh (Security & Identity)
- **Authentication:** Sử dụng **OAuth2 with Password Flow** và **JWT (JSON Web Token)**. Token được ký bằng thuật toán HS256 hoặc RS256.
- **Authorization:** Triển khai **Middleware RBAC** (Role-Based Access Control) chặn bắt mọi request để kiểm tra quyền hạn trước khi đi vào Controller.
- **Data Protection:** Mật khẩu người dùng được băm (Hash) bằng thuật toán **Bcrypt** với Salt ngẫu nhiên.
## 4. Cơ chế Tích hợp External Service (AI Integration)
Main Backend không trực tiếp thực hiện các tính toán AI. Thay vào đó, nó sử dụng **Adapter Pattern** để giao tiếp:
- **Module:** `app.services.external.ai_client`
- **Giao thức:** HTTP/REST (Synchronous) cho các dự báo nhanh, hoặc Message Queue (Asynchronous) cho các tác vụ train model.
- **Cơ chế Fallback:** Nếu AI Service không phản hồi (Timeout/Error), Main Backend sẽ trả về giá trị mặc định hoặc thông báo "Tính năng gợi ý tạm thời không khả dụng", đảm bảo luồng nghiệp vụ chính không bị gián đoạn (Graceful Degradation).
