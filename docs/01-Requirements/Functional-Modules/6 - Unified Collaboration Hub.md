**Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---
# 1. Business Overview
Trong các mô hình quản lý truyền thống, thông tin thường bị phân mảnh (Fragmented) rải rác khắp nơi: Email dùng để trao đổi chính thức, Zalo/Slack dùng để chat nhanh, và Google Drive dùng để lưu file. Điều này dẫn đến hiện tượng "Đảo thông tin" (Information Silos) và gia tăng chi phí chuyển đổi ngữ cảnh (Context Switching Cost).
Phân hệ **Unified Collaboration Hub** của PronaFlow được thiết kế để trở thành "Nguồn sự thật duy nhất" (Single Source of Truth) cho mọi hoạt động cộng tác. Triết lý thiết kế là **Contextual Communication** (Giao tiếp gắn liền ngữ cảnh): Mọi cuộc thảo luận, tài liệu phải được neo (anchor) trực tiếp vào đối tượng công việc (Task/Project) liên quan, thay vì trôi nổi trong các kênh chat chung chung.
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Contextual Threaded Discussions (Thảo luận theo luồng)
### User Story 6.1
Là một Thành viên dự án, Tôi muốn trao đổi, phản hồi về một Task cụ thể ngay trong giao diện của Task đó, Để toàn bộ lịch sử tranh luận và ra quyết định được lưu trữ tập trung, dễ dàng tra cứu lại sau này.
### Acceptance Criteria ( #AC)

#### AC 1 - Rich Text Editor (Trình soạn thảo văn bản)
- Hỗ trợ định dạng văn bản cơ bản (Bold, Italic, List, Code Block) để trình bày ý tưởng rõ ràng.
- Hỗ trợ dán ảnh trực tiếp từ Clipboard (Ctrl+V) để chia sẻ nhanh ảnh chụp màn hình lỗi (Bug screenshot).
#### AC 2 - Smart Mentions (@Tagging)
- **Interaction:** Khi người dùng gõ ký tự `@`, hệ thống hiển thị danh sách Dropdown gợi ý các thành viên **trong cùng dự án**.
- **Filtering:** Thuật toán sắp xếp ưu tiên hiển thị: Người đang được giao Task (Assignee) > Người báo cáo (Reporter) > Các thành viên tương tác gần đây.
- **Trigger:** Việc mention sẽ kích hoạt một sự kiện sang Module 7 (Notification System) để gửi thông báo tức thì cho người được nhắc.
#### AC 3 - Threaded Replies (Phản hồi phân cấp)
- Cho phép trả lời (Reply) một comment cụ thể, tạo thành một nhánh thảo luận con (Nested Thread). Điều này giúp giữ cho luồng thảo luận chính không bị loãng bởi các tranh luận chi tiết bên lề.
## 2.2. Feature: Digital Asset Management - DAM (Quản lý Tài sản số)
### User Story 6.2
Là một Designer, Tôi muốn tải lên các phiên bản thiết kế (v1, v2) đính kèm vào Task và xem trước chúng mà không cần tải về, Để các bên liên quan có thể góp ý trực quan.
### Acceptance Criteria (#AC)

#### AC 1 - Version Control (Kiểm soát phiên bản)
- **Behavior:** Khi người dùng tải lên một file có tên trùng với file đã tồn tại trong Task.
- **System Logic:** Hệ thống không ghi đè (Overwrite). Thay vào đó, nó tạo một bản ghi phiên bản mới (Versioning). User có thể xem lại lịch sử `v1`, `v2` và khôi phục nếu cần.
#### AC 2 - Universal Viewer (Trình xem trước đa năng)
- Tích hợp trình xem trước (Previewer) hỗ trợ các định dạng văn phòng phổ biến: PDF, DOCX, XLSX và các định dạng ảnh/video.
- **Security:** File chỉ được render trong Sandbox của trình duyệt, ngăn chặn thực thi mã độc.
## 2.3. Feature: Real-time Presence (Hiện diện thời gian thực)
### User Story 6.3
Là một Quản lý, Tôi muốn biết ai đang xem hoặc soạn thảo nội dung trên cùng một Task với tôi, Để tránh xung đột dữ liệu hoặc trùng lặp công việc.
### Acceptance Criteria ( #AC)
#### AC 1 - Visual Indicators
- Hiển thị Avatar của những người dùng đang mở Task đó ở góc trên màn hình (tương tự Google Docs).
- Hiển thị trạng thái "User A is typing..." dưới khung comment khi có người đang soạn thảo.
## 2.4. Feature: Formal Approval Workflow (Quy trình Phê duyệt Chính thức)

### User Story 6.4
Là một Stakeholder (Các bên liên quan), Tôi muốn thực hiện hành động "Phê duyệt" (Approve) hoặc "Từ chối" (Reject) đối với một tài liệu đính kèm hoặc kết quả công việc, Để hệ thống ghi nhận tính pháp lý của quyết định thay vì chỉ comment "OK" bằng lời.
### Acceptance Criteria ( #AC)
#### AC 1 - Decision State Machine (Máy trạng thái Quyết định)
- **Object:** Áp dụng cho File đính kèm (Attachments) hoặc Task.
- **Transitions:**
    1. `Pending Review`: Trạng thái mặc định khi yêu cầu phê duyệt.
    2. `Approved`: Khi người có thẩm quyền xác nhận. Hệ thống khóa (Lock) file/task lại, ngăn chỉnh sửa thêm để đảm bảo tính toàn vẹn.
    3. `Changes Requested`: Yêu cầu sửa đổi. Task tự động chuyển trạng thái về `In-Progress`.
#### AC 2 - Digital Signature Audit (Kiểm toán Chữ ký số)
- **Requirement:** Mỗi hành động phê duyệt phải được ghi lại với `Timestamp`, `User ID`, và `Checksum` của phiên bản tài liệu tại thời điểm phê duyệt.
- **Impact:** Đảm bảo tính chống chối bỏ (Non-repudiation). Nếu file bị thay đổi sau khi phê duyệt, trạng thái Approved phải tự động bị hủy bỏ (Invalidated).
## 2.5. Feature: Collaborative Search (Tìm kiếm Cộng tác)
### User Story 6.5
Là một Thành viên mới gia nhập dự án, Tôi muốn tìm kiếm các từ khóa trong toàn bộ lịch sử thảo luận và tài liệu, Để nhanh chóng nắm bắt bối cảnh (Context onboarding) mà không cần làm phiền đồng nghiệp cũ.
### Acceptance Criteria ( #AC)
#### AC 1 - Full-Text Search Scope
- **Scope:** Tìm kiếm quét qua cả 3 tầng dữ liệu:
    1. Nội dung Task (Title, Description).
    2. Nội dung Thảo luận (Comments, Replies).
    3. Nội dung File văn bản (Parse nội dung bên trong PDF, DOCX - _Tính năng nâng cao_).
#### AC 2 - Contextual Result Highlighting
- **Display:** Kết quả trả về phải hiển thị đoạn văn bản chứa từ khóa (Snippet) và link trực tiếp đến vị trí của comment đó trong luồng thảo luận (Deep Linking).

## 2.6. Feature: Project Notes (Wiki)
### User Story 6.6.
- Là một **Project Manager**
- Tôi muốn tạo các trang chi chú (Note) rich-text bên trong dự án và tổ chức chúng theo cấu trúc cây (Hierachy).
- Để lưu trữ các nội dung cần thiết như quy định, biên bản họp và tài liệu đặc tả ngay tại nơi làm việc mà không cần dùng GG Docs rời rạc.
### Acceptance Criteria ( #AC)
#### AC 1 - - **Rich Text Editor:** 
- Hỗ trợ soạn thảo văn bản định dạng (Bold, Italic, Heading, Checkbox) và nhúng ảnh (tương tự như mô tả trong Module 15).
#### **AC 2 - Hierarchy:** 
- Cho phép tạo ghi chú con (Nested Notes) không giới hạn cấp độ (Parent Note -> Child Note).
#### **AC 3 - Linkage:** 
- Cho phép `@mention` Task hoặc Project khác ngay trong nội dung ghi chú để tạo liên kết ngữ cảnh.
## 2.7. Feature: Personal Notes
### User Story 6.7.
- Là một Thành viên dự án.
- Tôi muốn có một khu vực ghi chú cá nhân riêng tư (Private Notes) truy cập nhanh từ Sidebar,
- Để ghi lại các ý tưởng tạm thời hoặc Todo list trong ngay trước khi chuyển đổi chúng thành Task chính thức.
### Acceptance Criteria ( #AC)
#### **AC 1 - Privacy:** 
- Dữ liệu này chỉ hiển thị với chính người dùng đó (Private by default).
#### **AC 2 - Convert to Task:** 
- Cung cấp nút "Convert to Task" để chuyển đổi nhanh một dòng ghi chú thành Task và chọn Project đích.
## 2.8. Feature: Note Templates
### User Story 6.8: 
- **Là một** Project Manager,
- **Tôi muốn** tạo và quản lý các mẫu ghi chú (Templates) như "Biên bản cuộc họp", "Báo cáo lỗi", "Đặc tả tính năng",
- **Để** cả team tuân thủ một chuẩn trình bày chung và tiết kiệm thời gian soạn thảo.
### **Acceptance Criteria (#AC):**
- **AC 1 - Template Library:** Hệ thống cung cấp sẵn thư viện mẫu (System Templates) và cho phép người dùng lưu một ghi chú bất kỳ thành mẫu riêng (Custom Templates).
- **AC 2 - Quick Apply:** Khi tạo Note mới, hiển thị popup: "Start with a template?". Khi chọn, nội dung mẫu sẽ được điền vào trình soạn thảo.
- **AC 3 - Variable Placeholders:** Hỗ trợ các biến giữ chỗ như `{{Current_Date}}`, `{{User_Name}}` để tự động điền dữ liệu khi áp dụng mẫu.
## 2.9. Feature: Public Publishing
### User Story 6.8: 
- **Là một** Chủ sở hữu dự án, 
- **Tôi muốn** xuất bản một trang ghi chú thành trang web công khai (Public Link),
- **Để** chia sẻ thông tin với khách hàng bên ngoài mà không cần mời họ vào Workspace (tiết kiệm license user).
### **Acceptance Criteria (#AC):**
#### **AC 1 - Generate Public Link:** 
- Tạo một URL ngẫu nhiên (hoặc tùy chỉnh slug) để truy cập ghi chú ở chế độ Read-only.
#### **AC 2 - Access Control:** 
- Tùy chọn đặt mật khẩu (Password Protection) hoặc thời hạn hết hạn (Expiration Date) cho link đó.
#### **AC 3 - Live Update:** 
- Khi nội dung gốc trong PronaFlow thay đổi, nội dung trên link public cũng tự động cập nhật theo (hoặc tùy chọn phải nhấn "Republish").
## 2.10. Feature: Document Versioning.
### User Story 6.10
- **Là một** Admin,
- **Tôi muốn** xem lại lịch sử thay đổi của tài liệu và biết ai đã sửa cái gì vào lúc nào,
- **Để** khôi phục lại phiên bản cũ nếu có sai sót hoặc tranh chấp nội dung.
### **Acceptance Criteria (#AC):**
#### **AC 1 - Auto-Snapshot:** 
- Hệ thống tự động lưu phiên bản (Snapshot) mỗi khi người dùng nhấn Save hoặc sau mỗi 10 phút soạn thảo liên tục.
#### **AC 2 - Diff View:** 
- Chế độ so sánh (Compare) làm nổi bật (Highlight) phần văn bản đã thêm (xanh) hoặc đã xóa (đỏ) giữa 2 phiên bản.
#### **AC 3 - Restore:** 
- Nút "Khôi phục phiên bản này" sẽ đưa nội dung hiện tại về trạng thái cũ.
## 2.11. Feature: Smart Backlinks
### **User Story 6.11.** 
- **Là một** Business Analyst,
- **Tôi muốn** nhìn thấy danh sách các trang hoặc Task đang nhắc đến trang hiện tại (Linked Mentions),
- **Để** đánh giá tác động (Impact Analysis) trước khi tôi sửa đổi nội dung trang này.
### **Acceptance Criteria (#AC):**
#### **AC 1 - Reference Detection:** 
- Hệ thống tự động quét và hiển thị danh sách "References" ở cuối trang Note.
#### **AC 2 - Unlinked Mentions:** 
- Gợi ý các từ khóa trong bài khớp với tên các Note khác nhưng chưa được tạo link, cho phép tạo link nhanh chỉ với 1 click.
# 3. Business Rules & Constraints
## 3.1. Quy tắc Bảo mật & Quyền riêng tư (Security & Privacy)
1. **Inherited Permissions (Quyền thừa kế):** Quyền truy cập vào Comment/File được thừa kế trực tiếp từ quyền truy cập Task.
    - Nếu User mất quyền truy cập Project, họ cũng mất quyền xem toàn bộ lịch sử thảo luận bên trong.
2. **Immutability Audit (Kiểm toán tính bất biến):**
    - Người dùng được phép chỉnh sửa (Edit) hoặc xóa (Delete) comment của chính mình.
    - **Tuy nhiên:** Hệ thống phải lưu lại lịch sử chỉnh sửa (`edited_at`, `original_content`) trong Database để phục vụ Audit Log. Không cho phép xóa vĩnh viễn dấu vết để đảm bảo tính minh bạch trong môi trường doanh nghiệp.
## 3.2. Ràng buộc về File (File Constraints)
1. **Storage Quota:** Giới hạn dung lượng tải lên dựa trên gói dịch vụ của Workspace (ví dụ: 100MB/file cho Free Plan, 1GB/file cho Enterprise).
2. **Allowed Extensions:** Chặn tuyệt đối các file thực thi (`.exe`, `.sh`, `.bat`, `.js`) ở tầng Backend để phòng chống Malware.
## 3.3. Ràng buộc về Hiệu năng Thời gian thực (Real-time Performance Constraints)
Để đảm bảo trải nghiệm "Cộng tác tức thì" (Instant Collaboration), hệ thống phải tuân thủ các chỉ số kỹ thuật (SLIs) sau:
1. **Message Delivery Latency:** Thời gian từ khi User A nhấn Enter đến khi User B nhìn thấy tin nhắn phải **< 200ms** (Ngưỡng nhận thức độ trễ của con người - _Human Perception Threshold_).
2. **Concurrency:** Hệ thống phải chịu tải được tối thiểu 50 người cùng thao tác (soạn thảo, comment) trên một Task tại cùng một thời điểm mà không gây ra xung đột dữ liệu (Data Race).
## 3.4. Quy tắc Lưu trữ Lạnh (Cold Storage Rule)
- Các file đính kèm của dự án đã đóng (Closed Project) quá 1 năm sẽ được tự động di chuyển từ ổ cứng SSD (Hot Storage) sang S3 Glacier (Cold Storage) để tối ưu chi phí hạ tầng.
- Việc truy xuất lại các file này sẽ có độ trễ (khoảng 3-5 giây để restore) thay vì tức thì.
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Lý thuyết về Độ giàu của Truyền thông (Media Richness Theory)
Lý thuyết này (Daft & Lengel, 1986) cho rằng hiệu quả giao tiếp phụ thuộc vào khả năng của kênh truyền tải trong việc xử lý thông tin phức tạp.
- **Ứng dụng trong PronaFlow:**
    - Sử dụng **Text Comment** cho các trao đổi thông tin xác thực, rõ ràng (Low ambiguity).
    - Sử dụng **Rich Media (Image/Video)** đính kèm cho các vấn đề phức tạp cần trực quan hóa (High ambiguity).
    - Sử dụng **Emoji/Reaction** để truyền tải cảm xúc và xác nhận nhanh (Ack) mà không tạo ra nhiễu thông báo (Noise reduction).
## 4.2. Giảm thiểu Chi phí Chuyển đổi Ngữ cảnh (Context Switching Cost)
Nghiên cứu của _Gerald Weinberg_ chỉ ra rằng mỗi khi chuyển đổi giữa các tác vụ hoặc ứng dụng, hiệu suất não bộ giảm khoảng 20-80%.
- **Giải pháp:** Bằng việc tích hợp "Unified Collaboration Hub" ngay trong màn hình chi tiết Task, PronaFlow loại bỏ nhu cầu phải `Alt+Tab` sang ứng dụng chat khác để hỏi "Cái này làm thế nào?". Mọi thứ cần thiết để hoàn thành công việc đều nằm trong tầm mắt (At hand), giúp duy trì trạng thái dòng chảy (Flow State) của nhân viên.
## 4.3. Hệ thống Bộ nhớ Giao dịch (Transactive Memory System - TMS)
Lý thuyết TMS (Wegner, 1987) cho rằng một nhóm làm việc hiệu quả không phải vì tất cả mọi người đều biết mọi thứ, mà vì họ biết "ai biết cái gì".
- **Áp dụng:** Tính năng **Smart Mentions** (AC 6.1) và **Collaborative Search** (AC 6.5) đóng vai trò là "bộ nhớ ngoài" (External Storage) của nhóm. Nó giúp giảm tải nhận thức cho từng cá nhân, vì họ không cần nhớ chi tiết sự việc, chỉ cần biết cách tra cứu nó trong PronaFlow.
## 4.4. Lý thuyết Phối hợp (Coordination Theory - Malone & Crowston)
Lý thuyết này định nghĩa phối hợp là "quản lý các sự phụ thuộc".
- **Áp dụng:** Tính năng **Formal Approval Workflow** (AC 6.4) giải quyết loại phụ thuộc "Nhà sản xuất/Người tiêu dùng" (Producer/Consumer dependency). Designer (Producer) cần sự phê duyệt của Client (Consumer) để tiến hành bước tiếp theo. Việc hệ thống hóa quy trình này giúp giảm thiểu độ trễ trong luồng công việc (Workflow Latency).