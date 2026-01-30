Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---
# 1. Business Overview
Trong vận hành hệ thống phần mềm doanh nghiệp, dữ liệu tăng trưởng theo hàm mũ theo thời gian. Việc giữ lại tất cả dữ liệu lịch sử trong cùng một không gian lưu trữ với dữ liệu hiện hành (Active Data) sẽ dẫn đến hai vấn đề nghiêm trọng:
1. **Suy giảm hiệu năng (Performance Degradation):** Kích thước bảng (Table Size) quá lớn làm tăng độ sâu của cây chỉ mục (B-Tree Index Depth), khiến các truy vấn SELECT/UPDATE trở nên chậm chạp.
2. **Rủi ro tuân thủ (Compliance Risk):** Các quy định quốc tế như GDPR (Châu Âu) yêu cầu doanh nghiệp phải có chính sách xóa dữ liệu rõ ràng (Right to be Forgotten) và khả năng trích xuất dữ liệu (Data Portability).
Module **Data Archiving & Compliance** của PronaFlow được thiết kế để giải quyết bài toán trên thông qua chiến lược **Lưu trữ Phân tầng (Tiered Storage)** và cơ chế **Quản trị Vòng đời Dữ liệu tự động**.
**Chiến lược Phân loại Dữ liệu:**
- **Hot Data:** Dữ liệu đang truy xuất thường xuyên (Dự án đang chạy). Yêu cầu độ trễ thấp (<100ms).
- **Warm Data:** Dữ liệu ít truy cập (Dự án vừa hoàn thành < 6 tháng).
- **Cold Data:** Dữ liệu lịch sử (Dự án > 6 tháng). Chuyển sang chế độ Read-only để tối ưu chi phí và hiệu năng.
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Automated Archiving Strategy
### User Story 8.1
Là một Quản trị viên hệ thống, Tôi muốn các dự án đã đóng (Closed) quá 6 tháng được tự động chuyển sang trạng thái lưu trữ lạnh, Để giảm tải cho cơ sở dữ liệu chính và tăng tốc độ truy vấn cho các dự án đang hoạt động.
### Acceptance Criteria ( #AC)
#### AC 1 - Trigger Condition
- **Given:** Một dự án có trạng thái `status = DONE` hoặc `CANCELLED`.
- **When:** Thời gian cập nhật cuối cùng (`last_activity_at`) vượt quá ngưỡng cấu hình (mặc định: 180 ngày).
- **Then:** Hệ thống chạy Background Job (Cronjob) để thực hiện quy trình lưu trữ (Archival Process).
#### AC 2 - State Transition & Immutability
- **System Behavior:**
    1. Cập nhật cờ `is_archived = true`.
    2. Chuyển dự án sang chế độ **Read-Only** (Chỉ đọc). Người dùng không thể thêm Task, Comment hay sửa đổi tài liệu.
    3. Hiển thị Badge "Archived" trên giao diện người dùng.
#### AC 3 - Query Isolation
- **Technical Requirement:** Các API lấy danh sách dự án mặc định (`GET /projects`) phải tự động lọc bỏ các dự án đã lưu trữ (trừ khi có tham số `include_archived=true`). Điều này đảm bảo Index Scan của Database luôn nhanh.
## 2.2. Feature: Trash Bin & Soft Delete
### User Story 8.2
Là một Người dùng, Tôi muốn có cơ chế "Thùng rác" lưu trữ tạm thời các mục đã xóa, Để tôi có thể khôi phục lại trong trường hợp xóa nhầm trước khi dữ liệu bị hủy vĩnh viễn.
### Acceptance Criteria (#AC)
#### AC 1 - Soft Delete Mechanism
- **Action:** Khi user chọn "Delete Task/Project".
- **System:** Không thực lệnh `DELETE` vật lý trong SQL. Thay vào đó, update `deleted_at = NOW()`. Dữ liệu biến mất khỏi giao diện chính nhưng vẫn tồn tại trong bảng.
#### AC 2 - Auto-Purge Policy (Chính sách tự hủy)
- **Rule:** Các mục trong thùng rác có thời gian lưu trữ tối đa là **30 ngày**.
- **Automation:** Hệ thống quét định kỳ mỗi ngày. Nếu `NOW() - deleted_at > 30 days` -> Thực hiện **Hard Delete** (Xóa vĩnh viễn khỏi ổ cứng).
#### AC 3 - Restore Capability
- **Action:** User truy cập giao diện Trash Bin và chọn "Restore".
- **Result:** Trường `deleted_at` được set về `NULL`. Dữ liệu xuất hiện trở lại tại vị trí cũ.

## 2.3. Feature: Data Export & Portability (Trích xuất dữ liệu)
### User Story 8.3
Là một Chủ sở hữu Workspace, Tôi muốn tải xuống toàn bộ dữ liệu dự án của mình dưới định dạng chuẩn (JSON/CSV), Để lưu trữ cục bộ hoặc di chuyển sang hệ thống khác (Tuân thủ quyền khả chuyển dữ liệu).
### Acceptance Criteria (#AC)
#### AC 1 - Async Export Processing
- **Constraint:** Vì lượng dữ liệu có thể rất lớn (hàng ngàn task), việc xuất dữ liệu không được thực hiện đồng bộ (Synchronous).
- **Flow:**
    1. User nhấn "Request Export".
    2. Server trả về thông báo "Đang xử lý".
    3. Worker Process thu thập dữ liệu, đóng gói thành file `.zip`.
    4. Hệ thống gửi Email chứa Secure Link tải xuống (Link hết hạn sau 24h).
#### AC 2 - Data Structure Standard
- **Format:** File xuất ra phải có cấu trúc JSON rõ ràng, bao gồm đầy đủ quan hệ: Projects -> Lists -> Tasks -> Comments/Attachments.
# 3. Business Rules & Compliance Standards
## 3.1. Quy tắc Toàn vẹn Tham chiếu khi Xóa (Referential Integrity on Delete)
Khi thực hiện xóa vĩnh viễn (Hard Delete) một thực thể cha, hệ thống phải tuân thủ quy tắc **Cascading Delete** để tránh dữ liệu rác (Orphaned Data)
- Xóa `Project` -> Xóa toàn bộ `Task Lists`, `Tasks`, `Comments`, `File Metadata` liên quan.
- **Ngoại lệ:** Đối với `User`, khi người dùng xóa tài khoản, các `Comments` và `Activity Logs` của họ **KHÔNG** bị xóa mà chỉ được ẩn danh (Anonymization).
    - _Lý do:_ Để bảo toàn ngữ cảnh lịch sử của dự án cho các thành viên còn lại. Tên hiển thị sẽ chuyển thành "Deleted User".
## 3.2. Data Retention Policy (Chính sách lưu trữ)
Chính sách này được thiết lập cứng trong hệ thống để đảm bảo tính pháp lý:

|Loại Dữ Liệu|Thời gian lưu trữ|Hành động sau khi hết hạn|Mục đích|
|---|---|---|---|
|**Deleted Items**|30 ngày|Hard Delete|Hỗ trợ khôi phục lỗi thao tác (User Error).|
|**System Logs**|90 ngày|Archive to Cold Storage|Phục vụ Audit (Kiểm toán) và Debug.|
|**User Uploads**|Theo vòng đời dự án|Xóa khi Project bị xóa|Tối ưu chi phí lưu trữ S3/Disk.|

# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Tối ưu hóa B-Tree Index (Cơ sở Khoa học Máy tính)
Hầu hết các RDBMS (như PostgreSQL sử dụng trong PronaFlow) dùng cấu trúc B-Tree cho chỉ mục.
- **Vấn đề:** Chi phí tìm kiếm là $O(\log N)$. Khi $N$ (số bản ghi) tăng quá lớn, dù là hàm logarit, độ sâu của cây vẫn tăng, làm tăng I/O đĩa.
- **Giải pháp Archiving:** Việc di chuyển dữ liệu cũ sang bảng Archive hoặc Partition khác giúp giữ $N$ của bảng chính (Hot Table) ở mức thấp và ổn định. Điều này đảm bảo hiệu năng hệ thống không bị suy thoái theo thời gian (System aging).
## 4.2. Tuân thủ GDPR (General Data Protection Regulation)
Module này được thiết kế để đáp ứng các điều khoản cụ thể của luật bảo vệ dữ liệu Châu Âu (tiêu chuẩn vàng về bảo mật):
- **Right to Erasure (Art. 17):** Đáp ứng qua tính năng _Hard Delete_ và _Auto-Purge_.
- **Right to Data Portability (Art. 20):** Đáp ứng qua tính năng _Data Export (JSON)_.
- **Storage Limitation (Art. 5(1)(e)):** Đáp ứng qua _Data Retention Policy_ (Không lưu trữ dữ liệu lâu hơn mức cần thiết).