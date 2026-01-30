**Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---
# 1. Nhóm Định nghĩa Hằng số (Constants & Enums)
Danh cho Dev copy vào code (Frontend/Backend) để mapping

| **Tên File Đề xuất**           | **Định dạng**  | **Nội dung trích xuất từ** | **Mục đích hiển thị**                                                                                                                       |
| ------------------------------ | -------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **`project-statuses.json`**    | JSON           |                            | **Danh sách trạng thái dự án:**<br>Chứa ID, Tên hiển thị (VN/EN), Mã màu Hex. Dev không cần đoán màu hay ID nữa.                            |
| **`task-priorities.json`**     | JSON           |                            | **Độ ưu tiên & SLA:**<br>Quy định rõ: `Urgent` = 4h, `High` = 8h. Dùng để tính toán deadline tự động.                                       |
| **`subscription-quotas.yaml`** | YAML           |                            | **Hạn mức gói cước:**<br>Quy định rõ: Gói `Free` (3 projects, 5 members), `Pro` (Unlimited). Dùng cho logic chặn người dùng (Enforcement).  |
| **`system-error-codes.md`**    | Markdown Table | [[system-error-codes]]     | **Bảng mã lỗi chuẩn:**<br>Ví dụ: `ERR_001`: Sai mật khẩu, `ERR_429`: Quá giới hạn request. Giúp Frontend hiển thị thông báo lỗi thống nhất. |

# 2. Nhóm Cấu hình Mặc định (Default Configurations)
Dành cho việc khởi tạo hệ thống hoặc onboarding người dùng mới.

| **Tên File Đề xuất**                      | **Định dạng** | **Nội dung trích xuất từ** | **Mục đích hiển thị**                                                                                                          |
| ----------------------------------------- | ------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **`default-user-settings.json`**          | JSON          |                            | **Cài đặt mặc định:**<br>Theme: `light`, Language: `vi-VN`, Font-size: `14px`. Dùng khi tạo user mới.                          |
| **`notification-templates-library.json`** | JSON          | [[]]                       | **Kho mẫu thông báo:**<br>Chứa các câu văn mẫu cho Email/Push. Ví dụ: `TASK_ASSIGNED`: "Bạn vừa được giao việc {{task_name}}". |
| **`data-retention-rules.csv`**            | CSV           | [[]]                       | **Quy tắc lưu trữ:**<br>Dòng 1: `Trash Bin`, `30 days`. Dòng 2: `Audit Log`, `90 days`. Dùng cho các Cronjob dọn dẹp DB.       |

# 3. Nhóm Quy định Kỹ thuật (Technical Governance)
Dành cho Dev tuân thủ quy tắc đặt tên và cấu trúc.

| **Tên File Đề xuất**           | **Định dạng** | **Nội dung trích xuất từ** | **Mục đích hiển thị**                                                                                                               |
| ------------------------------ | ------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **`api-endpoints-catalog.md`** | Markdown List |                            | **Danh mục API:**<br>Liệt kê nhanh các route: `POST /auth/login`, `GET /projects`, `POST /tasks`. Giúp Dev nhìn nhanh cấu trúc URL. |
| **`permission-scopes.yaml`**   | YAML          |                            | **Danh sách Quyền (Scope):**<br>Định nghĩa các string quyền như `task:read`, `task:write`, `user:delete`. Dùng trong JWT Token.     |

# Nhóm Dữ liệu & AI
Dành cho Data Scientist

| **Tên File Đề xuất**              | **Định dạng** | **Vị trí lưu**               | **Mục đích & Nội dung**                                                                                                                                                                                                                     |
| --------------------------------- | ------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`data-dictionary.csv`**         | CSV           | `docs/07-References/`        | **Từ điển Dữ liệu:**<br>Giải thích ý nghĩa từng trường trong Database.<br>_Cấu trúc:_ `Table`, `Column`, `Data Type`, `Business Meaning`, `Formula (nếu có)`.<br>_Ví dụ:_ `tasks`, `story_points`, `int`, "Độ phức tạp dựa trên Fibonacci". |
| **`feature-store-registry.yaml`** | YAML          | `docs/04-AI-Specifications/` | **Kho đặc trưng AI (Feature Store):**<br>Liệt kê các biến đầu vào cho Model.<br>_Ví dụ:_<br>`- name: assignee_overdue_rate`<br>`type: float`<br>`source: module_11`<br>`description: "Tỷ lệ trễ hạn trong 3 tháng qua"`                     |
| **`metric-definitions.md`**       | Markdown      | `docs/11-Analytics/`         | **Định nghĩa chỉ số báo cáo:**<br>Công thức tính toán chính xác để Dev và Data Analyst không cãi nhau.<br>_Ví dụ:_ "Active User = User có ít nhất 1 action trong 7 ngày (không tính login)".                                                |

# Nhóm Kỹ thuật & DevOps
Dành cho Dev, giúp code đồng nhất.

| **Tên File Đề xuất**          | **Định dạng** | **Vị trí lưu**        | **Mục đích & Nội dung**                                                                                                                                                                          |
| ----------------------------- | ------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`.env.example`**            | Text          | Root project          | **Mẫu biến môi trường:**<br>Liệt kê TẤT CẢ các key config cần thiết (nhưng để value rỗng hoặc fake).<br>_Ví dụ:_ `DB_HOST=localhost`, `JWT_SECRET=changeme`, `AI_SERVICE_URL=...`                |
| **`git-convention.md`**       | Markdown      | Root project          | **Quy tắc Commit Code:**<br>Quy định format message.<br>_Ví dụ:_ `feat: add login`, `fix: task drag drop error`, `docs: update readme`.                                                          |
| **`api-response-codes.json`** | JSON          | `docs/07-References/` | **Bảng mã lỗi chuẩn (Frontend mapping):**<br>Mapping mã lỗi Backend sang câu thông báo UI.<br>_Ví dụ:_ `{ "AUTH_001": "Sai mật khẩu", "PROJ_403": "Bạn không có quyền truy cập dự án này" }`.    |
| **`keyboard-shortcuts.json`** | JSON          | `docs/07-References/` | **Danh sách phím tắt (Cho Module 9):**<br>File này Frontend có thể load trực tiếp để hiển thị bảng "Cheatsheet" cho người dùng.<br>_Ví dụ:_ `{ "ctrl+n": "create_task", "esc": "close_modal" }`. |

# Nhóm UI/UX & Nội dung
Dành cho Designer & Marketing, đảm bảo giao diện và ngôn ngữ nhất quán.

| **Tên File Đề xuất**        | **Định dạng** | **Vị trí lưu**          | **Mục đích & Nội dung**                                                                                                                                                                     |
| --------------------------- | ------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`glossary.json`**         | JSON          | `docs/00-General/`      | **Thuật ngữ hệ thống (Tooltip):**<br>Định nghĩa các từ chuyên ngành để hiển thị Tooltip giải thích trên UI.<br>_Ví dụ:_ `{ "term": "Sprint", "def": "Chu kỳ làm việc ngắn hạn 1-4 tuần" }`. |
| **`iconography-map.md`**    | Table         | `docs/03-UI-UX-Design/` | **Quy định Icon:**<br>Mapping giữa hành động và tên Icon (Lucide/FontAwesome).<br>_Ví dụ:_ `Edit` -> `pencil-alt`, `Delete` -> `trash-2`. Tránh việc chỗ dùng cái này chỗ dùng cái kia.     |
| **`email-signatures.html`** | HTML          | `assets/templates/`     | **Chữ ký Email tự động:**<br>Mẫu HTML chuẩn cho các email gửi ra từ hệ thống (Module 7).                                                                                                    |

# Nhóm Kiểm thử (QA/Testing)
Dành cho việc bắt lỗi trước khi release

| **Tên File Đề xuất**          | **Định dạng** | **Vị trí lưu**               | **Mục đích & Nội dung**                                                                                                  |
| ----------------------------- | ------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **`test-case-standard.xlsx`** | Excel         | `docs/06-Quality-Assurance/` | **Mẫu Test Case chuẩn:**<br>Cột: `Test ID`, `Scenario`, `Steps`, `Expected Result`, `Actual Result`, `Pass/Fail`.        |
| **`security-checklist.md`**   | Checkbox      | `docs/06-Quality-Assurance/` | **Danh sách kiểm tra bảo mật:**<br>`[ ] API không lộ stack trace`, `[ ] Input đã sanitize`, `[ ] CORS được config đúng`. |