Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---
# 1. Business Overview
Trong một hệ thống cộng tác thời gian thực như PronaFlow, việc thông báo kịp thời là yếu tố sống còn. Tuy nhiên, ranh giới giữa "Thông tin hữu ích" và "Spam" rất mong manh. Một hệ thống tồi sẽ gửi email cho mỗi lần sửa lỗi chính tả, dẫn đến hiện tượng **Mệt mỏi vì thông báo (Notification Fatigue)**.
Phân hệ số 7 được xây dựng dựa trên kiến trúc **Event-Driven Architecture (EDA)**. Thay vì các Module gọi nhau trực tiếp (Synchronous), chúng sẽ phát ra các sự kiện (Events) vào một Message Broker trung gian (Redis/RabbitMQ). Notification Service đóng vai trò là "Consumer", lắng nghe, lọc, gộp và phân phối thông báo đến người dùng qua kênh phù hợp nhất.
**Mục tiêu thiết kế:** "Đúng người - Đúng lúc - Đúng kênh" (Right Person, Right Time, Right Channel).
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Intelligent Aggregation (Gộp thông báo thông minh)
### User Story 7.1
Là một Người dùng bận rộn, Tôi muốn nhận được một thông báo tóm tắt thay vì hàng loạt thông báo rời rạc khi ai đó thực hiện nhiều thao tác nhỏ liên tiếp, Để hộp thư của tôi không bị quá tải (Inbox Zero).
### Acceptance Criteria (#AC)
#### AC 1 - Debounce Logic (Thuật toán chống rung)
- **Scenario:** User A sửa Title, sau đó sửa Description, rồi đổi Due Date của cùng một Task trong vòng 1 phút.
- **System Behavior:** Hệ thống không gửi 3 thông báo. Nó chờ một khoảng thời gian đệm (Buffer Time, ví dụ: 2 phút). Sau khi không có hành động mới, nó gửi 1 thông báo duy nhất: _"User A đã cập nhật 3 thuộc tính của Task X"_.
#### AC 2 - Batching (Gom nhóm)
- **Display:** Trong menu thông báo In-app, các thông báo cùng loại phải được nhóm lại.
    - _Bad:_ `[Dòng 1: A like comment]`, `[Dòng 2: B like comment]`, `[Dòng 3: C like comment]`.
    - _Good:_ "A, B và C đã thích bình luận của bạn."
## 2.2. Feature: Real-time Delivery & Fallback (Chuyển phát thời gian thực & Dự phòng)
### User Story 7.2
Là một Người quản lý, Tôi muốn biết ngay lập tức khi một dự án chuyển sang trạng thái "Rủi ro", nhưng nếu tôi không online, hãy gửi email cho tôi.
### Acceptance Criteria ( #AC)
#### AC 1 - Presence Awareness Routing (Định tuyến theo hiện diện)
- **Logic:**
    - IF `User.is_online == true`: Gửi qua **WebSocket** (Toast Notification góc màn hình). Không gửi Email.
    - IF `User.is_online == false`: Gửi qua **Email** hoặc **Mobile Push**.
- **Benefit:** Tránh làm phiền người dùng bằng email khi họ đang ngồi ngay trước màn hình ứng dụng.
#### AC 2 - Ephemeral vs. Persistent (Tạm thời vs. Vĩnh viễn)
- Các thông báo dạng "Toast" (User A đang nhập liệu...) là tạm thời (Ephemeral), không lưu vào Database.
- Các thông báo nghiệp vụ (User A gán task cho bạn) là vĩnh viễn (Persistent), phải lưu vào Database để xem lại trong History.
## 2.3. Feature: Unsubscribe Strategy (Chiến lược Hủy đăng ký)
### User Story 7.3
Là một Người dùng, Tôi muốn dễ dàng tắt thông báo từ một Task cụ thể mà tôi không còn quan tâm, ngay cả khi tôi vẫn là thành viên dự án.
### Acceptance Criteria (#AC)
#### AC 1 - Granular Subscription
- Mỗi Task/Project có một nút "Watch/Unwatch" (hình con mắt).
- Hệ thống tôn trọng quyền này cao hơn quyền thành viên. Nếu User chọn "Unwatch", họ sẽ không nhận thông báo trừ khi được @mention trực tiếp.

## 2.4. Feature: Notification Templating Engine (Công cụ Quản lý Mẫu)

### User Story 7.4

Là một System Admin, Tôi muốn định nghĩa nội dung thông báo thông qua các mẫu (Templates) hỗ trợ đa ngôn ngữ và biến động, Để dễ dàng thay đổi nội dung marketing hoặc cảnh báo hệ thống mà không cần sửa code (Hard-code) và deploy lại server.

### Acceptance Criteria (#AC)

#### AC 1 - Variable Injection (Tiêm biến)

- **Mechanism:** Sử dụng cú pháp Mustache hoặc Jinja2.
    
    - _Template:_ `Hello {{user_name}}, task {{task_title}} is due in {{hours}} hours.`
        
    - _Data:_ `{user_name: "Truc", task_title: "Fix Bug UI", hours: 2}`
        
    - _Output:_ "Hello Truc, task Fix Bug UI is due in 2 hours."
        

#### AC 2 - Localization Support (Hỗ trợ Đa ngữ)

- Hệ thống tự động chọn Template phù hợp dựa trên cài đặt ngôn ngữ (`user_lang`) của người nhận (Receiver).
    
- Nếu không tìm thấy mẫu tiếng Việt, tự động fallback về tiếng Anh.
    

## 2.5. Feature: Interaction Tracking (Theo dõi Tương tác)

### User Story 7.5

Là một Product Manager, Tôi muốn biết tỷ lệ mở (Open Rate) và tỷ lệ click (CTR) của các thông báo, Để đánh giá hiệu quả của hệ thống và tinh chỉnh chiến lược gửi tin.

### Acceptance Criteria (#AC)

#### AC 1 - Read Receipts (Báo đã xem)

- **Logic:** Khi người dùng mở danh sách thông báo hoặc click vào thông báo Toast.
    
- **Action:** Gửi sự kiện `mark_as_read` lên server. Biểu tượng "chấm đỏ" (Unread Badge) phải biến mất tức thì trên tất cả các thiết bị khác của người dùng đó (Cross-device Sync).
    

#### AC 2 - Actionable Notifications

- Cho phép đính kèm hành động nhanh (Quick Actions) ngay trong thông báo Push/Email (ví dụ: nút "Approve", "Reply").
    
- Ghi nhận log khi người dùng tương tác qua các nút này.
# 3. Business Rules & Technical Constraints
## 3.1. Cơ chế Thử lại (Retry Mechanism & Exponential Backoff)
Do phụ thuộc vào các dịch vụ bên thứ 3 (SMTP Server cho Email, Firebase cho Push), việc gửi thất bại là điều không tránh khỏi.
- **Rule:** Nếu gửi Email thất bại, hệ thống phải tự động thử lại tối đa 3 lần.
- **Backoff:** Thời gian chờ giữa các lần thử tăng theo cấp số nhân: 1s -> 5s -> 25s. Nếu sau 3 lần vẫn lỗi -> Ghi log lỗi và đánh dấu thông báo là "Failed".
## 3.2. Tính chất Idempotency (Bất biến)
- **Vấn đề:** Trong kiến trúc phân tán, một sự kiện có thể bị gửi trùng lặp (Duplicate Events).
- **Giải pháp:** Notification Service phải kiểm tra `Event_ID`. Nếu `Event_ID` này đã được xử lý, hệ thống phải bỏ qua để đảm bảo người dùng không bao giờ nhận 2 email giống hệt nhau.
## 3.3. Bảo mật nội dung (Security)

- **Email Body:** Không bao giờ chứa thông tin nhạy cảm (Mật khẩu, Dữ liệu tài chính) trong nội dung Email. Chỉ gửi đường dẫn an toàn (Secure Link) trỏ về ứng dụng PronaFlow.
## 3.4. Quy tắc Hàng đợi Ưu tiên (Priority Queues & QoS)

Không phải tất cả thông báo đều bình đẳng. Hệ thống phân chia 3 làn đường xử lý (Processing Lanes):
1. **High Priority (Critical):** Cảnh báo bảo mật, Lỗi hệ thống, SLA Breach.
    - _QoS:_ Gửi ngay lập tức (< 1s). Bỏ qua logic Debounce.
2. **Medium Priority (Transactional):** Mention, Task Assignment.
    - _QoS:_ Gửi trong vòng 5-10s. Áp dụng Debounce.
3. **Low Priority (Promotional/Bulk):** Bản tin tuần (Weekly Digest), Lời nhắc chung.
    - _QoS:_ Xử lý khi tài nguyên rảnh rỗi (Background Jobs).
## 3.5. Quy tắc TTL (Time-To-Live)
- Đối với các thông báo có tính thời điểm (ví dụ: "Cuộc họp bắt đầu trong 5 phút"), nếu vì lý do kỹ thuật mà sau 30 phút mới gửi được, hệ thống phải **Hủy bỏ (Discard)** thông báo đó.
- _Lý do:_ Việc nhận thông báo họp khi cuộc họp đã kết thúc gây trải nghiệm tiêu cực (Negative UX).
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Mô hình Observer (Observer Pattern - GoF)
Đây là Design Pattern nền tảng cho module này.
- **Subject:** Là các thực thể nghiệp vụ (Task, Project).
- **Observer:** Là các User đang theo dõi (Watchers).
- **Lợi ích:** Giảm sự phụ thuộc chặt chẽ (Decoupling). Module "Quản lý Task" không cần biết ai đang theo dõi nó, nó chỉ cần bắn sự kiện "Task Updated". Module Notification sẽ lo phần còn lại.
## 4.2. Lý thuyết Tín hiệu (Signal Detection Theory)
Lý thuyết này phân biệt giữa "Tín hiệu" (Thông tin quan trọng) và "Nhiễu" (Thông tin vô giá trị).
- **Áp dụng:** Các tính năng _Debounce_ và _Aggregation_ (AC 7.1) được thiết kế để tăng **Tỷ lệ Tín hiệu trên Nhiễu (Signal-to-Noise Ratio)**. Một hệ thống có tỷ lệ này cao sẽ gia tăng lòng tin của người dùng; ngược lại, họ sẽ phớt lờ hoặc tắt toàn bộ thông báo (Desensitization).
## 4.3. Mô hình Hành vi Fogg (Fogg Behavior Model)
$$B = MAP$$
(Behavior = Motivation + Ability + Prompt).
- **Prompt (Lời nhắc):** Thông báo chính là Prompt.
- **Áp dụng:** Để thông báo dẫn đến hành động (ví dụ: Vào review code), nó phải xuất hiện khi người dùng có đủ Động lực và Khả năng. Việc _Routing theo hiện diện_ (AC 7.2) đảm bảo Prompt xuất hiện ở nơi người dùng dễ tiếp cận nhất (Ability cao nhất), làm tăng xác suất chuyển đổi hành vi.
## 4.4. Định luật Hick về Phản hồi (Hick's Law in Feedback)
Mặc dù Định luật Hick thường nói về việc ra quyết định, trong ngữ cảnh thông báo, nó liên quan đến **Độ phức tạp của hành động**.
- **Áp dụng:** Tính năng _Actionable Notifications_ (AC 7.5) giúp giảm thiểu số bước thao tác. Thay vì phải [Click thông báo -> Chờ mở App -> Tìm nút Approve], người dùng có thể Approve ngay từ màn hình khóa. Điều này giảm "ma sát" (Friction), tăng tốc độ phản hồi chung của quy trình cộng tác.
## 4.5. Mô hình CAP (CAP Theorem) trong Thiết kế Phân tán
Đối với Notification System, chúng ta ưu tiên **Availability (Tính sẵn sàng)** và **Partition Tolerance (Khả năng chịu lỗi phân vùng)** hơn là Consistency (Tính nhất quán tức thì).
- **Giải thích:** Chấp nhận việc trạng thái "Đã đọc" có thể không đồng bộ tức thì giữa Mobile và Desktop trong vài giây (Eventual Consistency), miễn là thông báo luôn được gửi đi thành công.