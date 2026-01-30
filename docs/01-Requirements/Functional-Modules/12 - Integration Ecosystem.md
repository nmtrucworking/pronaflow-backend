**Project**: PronaFlow
**Version**: 1.0
**State**: 
***Last updated:** Dec 31, 2025*

---
# 1. Business Overview.
Trong môi trường phát triển hiện đại, không một công cụ nào có thể làm tốt tất cả mọi việc. Một đội ngũ kỹ thuật thường sử dụng kết hợp nhiều công cụ chuyên biệt (Best-of-breed tools):
	**GitLab/GitHub** để quản lý mã nguồn, 
	**Figma** để thiết kế, 
	**Slack/Discord** để giao tiếp 
	**Google Calendar** để quản lý lịch họp.
Phân hệ *Integration Ecosystem* được xây dựng để phá vỡ các Data Silos này. Thay vì bắt người dùng phải chuyển đổi liên tục giữa các tab trình duyệt, PronaFlow đóng vai trò là Command Center, nơi dữ liệu từ phần mềm xung quanh được đồng bộ và hiển thị tập trung.
Chiến lược tích hợp của PronaFlow bao gồm 3 tầng:
1. **Core Connectors:** Các tích hợp được xây dựng sẵn (Native Built-in) bởi đội ngũ PronaFlow.
2. **Open API & Webhooks:** Cung cấp cổng giao tiếp cho các nhà phát triển bên thứ 3 tự xây dựng giải pháp.
3. **Marketplace:** Nơi cộng đồng chia sẻ các tiện ích mở rộng (Plugins/Add-ons).
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Public RESTful API
### User Story 12.1
Là một DevOps Engineer, Tôi muốn viết một script tự động tạo Task trên PronaFlow mỗi khi pipeline CI/CD bị lỗi, Để đội ngũ phát triển nhận biết và xử lý ngay lập tức mà không cần báo cáo thủ công.
### Acceptance Criteria (#AC)
#### AC 1 - Standardized Endpoints
- Cung cấp đầy đủ các endpoint CRUD cho các tài nguyên chính: `/api/v1/projects`, `/api/v1/tasks`, `/api/v1/comments`.
- Tuân thủ chuẩn REST: Sử dụng đúng HTTP Methods (GET, POST, PATCH, DELETE) và Status Codes (200, 201, 400, 401).
#### AC 2 - Interactive Documentation (Swagger UI)
- Tích hợp **OpenAPI Specification (Swagger)**.
- Cho phép lập trình viên "Try it out" (gọi thử API) ngay trên trang tài liệu với tài khoản sandbox.
#### AC 3 - Authentication via Personal Access Token (PAT)
- Người dùng có thể tạo, đặt tên và thu hồi các PAT trong phần cài đặt cá nhân.
- PAT phải có phạm vi quyền hạn (Scopes) rõ ràng (ví dụ: chỉ có quyền `read:tasks`, không có quyền `delete:projects`).
## 2.2. Feature: Outbound Webhooks
### User Story 12.2
Là một Quản trị viên hệ thống, Tôi muốn PronaFlow gửi một thông báo HTTP POST đến server nội bộ của công ty mỗi khi một Task chuyển sang trạng thái "Done", Để kích hoạt quy trình thanh toán tự động cho Freelancer.
### Acceptance Criteria (#AC)
#### AC 1 - Event Triggers
- Hỗ trợ đăng ký nhận sự kiện cho các hành động: `task.created`, `task.status_changed`, `comment.created`.
- Cho phép người dùng cấu hình Payload URL và Secret Key (để ký xác thực HMAC).
#### AC 2 - Delivery Reliability (Độ tin cậy chuyển phát)
- **Retry Mechanism:** Nếu server đích trả về lỗi (5xx) hoặc Timeout, hệ thống tự động thử lại (Exponential Backoff) tối đa 5 lần trước khi báo lỗi.
- **Log History:** Lưu lịch sử các lần gửi Webhook (Request Header, Body, Response) để người dùng debug.
## 2.3. Feature: Native Connectors (Đầu nối dựng sẵn)
### User Story 12.3
Là một Project Manager, Tôi muốn đồng bộ ngày hạn (Due Date) của các Task trong PronaFlow vào Google Calendar của tôi, Để tôi không bị lỡ lịch trình khi đang xem lịch trên điện thoại.
### Acceptance Criteria (#AC)
#### AC 1 - OAuth2 Authorization Flow
- Người dùng chỉ cần click "Connect Google Calendar" -> Chuyển hướng sang trang đăng nhập Google -> Cấp quyền -> Quay lại PronaFlow. Tuyệt đối không yêu cầu người dùng nhập Password Google.
#### AC 2 - Bi-directional Sync (Đồng bộ 2 chiều) - _Advanced_
- **PronaFlow -> Calendar:** Khi tạo Task có Due Date, tự động tạo Event trên Calendar.
- **Calendar -> PronaFlow:** Khi dời lịch Event trên Calendar, tự động cập nhật Due Date của Task tương ứng.
### User Story 12.4
Là một Developer, Tôi muốn khi tôi commit code lên GitHub với message "Fix #123", Task số #123 trên PronaFlow tự động chuyển trạng thái sang "In Review" và đính kèm link commit vào phần comment.
### Acceptance Criteria (#AC)
#### AC 1 - Commit Linking
- Hệ thống lắng nghe Webhook từ GitHub.
- Regex parse commit message để tìm Pattern `#{TaskID}`.
#### AC 2 - Smart Transition
- Tự động thực hiện chuyển trạng thái (State Transition) dựa trên từ khóa (Fix, Close, Resolve -> Done/In Review).
## 2.4. Feature: Plugin Architecture (Kiến trúc Plugin)
### User Story 12.5
Là một Đối tác phát triển, Tôi muốn xây dựng một Plugin hiển thị bản đồ địa lý (GIS Map) ngay trong giao diện Task của PronaFlow, Để phục vụ các khách hàng trong lĩnh vực Logistics.
### Acceptance Criteria (#AC)
#### AC 1 - Manifest File
- Mỗi Plugin được định nghĩa bởi file `manifest.json` chứa metadata: Tên, Phiên bản, Quyền truy cập cần thiết, Điểm neo giao diện (UI Anchor Points - ví dụ: `task_detail_sidebar`, `project_header`).
#### AC 2 - Sandboxed Execution
- Plugin chạy trong môi trường cô lập (Iframe hoặc Web Worker) để đảm bảo an toàn. Plugin không được phép truy cập trực tiếp vào LocalStorage hay Cookie của ứng dụng chính.
- Giao tiếp với PronaFlow Core thông qua **SDK Bridge** (postMessage API).
# 3. Business Rules & Technical Constraints
## 3.1. Rate Limiting (Giới hạn tần suất)
Để bảo vệ hệ thống khỏi các cuộc tấn công DDoS hoặc lỗi code từ bên thứ 3 (Infinite Loop):
- **Quy tắc:** Giới hạn mỗi User/Token chỉ được gọi tối đa **1000 requests/phút** (đối với gói Pro) và **60 requests/phút** (đối với gói Free).
- **Phản hồi:** Trả về HTTP 429 (Too Many Requests) kèm header `Retry-After` khi vượt quá giới hạn.
## 3.2. Data Security & Consent
- **Quy tắc:** Không bao giờ chia sẻ dữ liệu người dùng cho bên thứ 3 nếu không có sự đồng ý rõ ràng (Explicit Consent) thông qua màn hình cấp quyền OAuth.
- **Revocation:** Người dùng có quyền thu hồi quyền truy cập (Revoke Access) của bất kỳ ứng dụng nào bất kỳ lúc nào tại trang "Connected Apps".
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. API Economy (Nền kinh tế API)
PronaFlow không chỉ bán phần mềm, mà bán khả năng kết nối. Việc mở API giúp PronaFlow trở thành một Platform, tận dụng sức sáng tạo của cộng đồng để lấp đầy những tính năng ngách (Niche Features) mà đội ngũ core team không đủ nguồn lực để làm (ví dụ: Tích hợp với phần mềm kế toán địa phương).
## 4.2. Loose Coupling (Liên kết lỏng)
Kiến trúc tích hợp qua Webhooks và API đảm bảo nguyên tắc **Loose Coupling**.
- Nếu GitHub thay đổi giao diện, tích hợp của PronaFlow không bị ảnh hưởng miễn là GitHub API không đổi.
- Hệ thống PronaFlow vẫn hoạt động bình thường ngay cả khi dịch vụ bên thứ 3 (như Slack) bị sập.
## 4.3. Event-Driven Architecture (EDA)
Webhooks là hiện thân của EDA. Thay vì bắt bên thứ 3 phải liên tục hỏi "Có gì mới không?" (Polling) gây lãng phí tài nguyên, PronaFlow chủ động thông báo "Có cái này mới!" (Push). Điều này giúp giảm độ trễ thông tin xuống gần như bằng 0 (Real-time).
