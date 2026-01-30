**Project**: PronaFlow
**Version**: 1.0
**State**: 
***Last updated:** Dec 31, 2025*

---
# 1. Business Overview
Trong quản trị dự án hiện đại, dữ liệu không chỉ là những con số vô tri mà là tài sản cốt lỗi để tối ưu hóa vận hành. Các nhà quản lý thường gặp khó khăn khi phải tổng hợp thủ công dữ liệu từ nhiều nguồn (Exel, Chat, Email) để làm báo cáo tiến độ, dẫn đến độ trễ thông tin và sai lệch số liệu.
Module `Advanced Analytics & Reporting` của PronaFlow tập trung vào **Descriptive Analytics*** và **Diagnostic Analytics***. Mục tiêu là cung cấp một bức tranh toàn cảnh, minh bạch về Project-Health thông qua các chỉ số định lượng chính xác, giúp trả lời câu hỏi: "*Điều gì đã xảy ra và Tại sao?*".
Module này cũng đóng vai trò là nguồn dữ liệu đầu vào cho Module 13 thông qua tính năng Time Tracking.
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Agile Performance Metrics (Chỉ số Hiệu suất Agile)
### User Story 11.1
Là một Scrum Master, Tôi muốn xem biểu đồ Burn-down và Burn-up tự động cập nhật theo thười gian thực, Để đánh giá xem team có khả năng hoàn thành Sprint đúng hạn hay không mà không cần vẽ tay.
### Acceptance Criteria ( #AC)
#### AC 1 - Real-time Calculation:
- Input: Dữ liệu từ các thay đổi trạng thái Task và cập nhật Remaining Work.
- **Visualization:**
    - **Ideal Line:** Đường lý tưởng (tuyến tính từ tổng điểm Story Points về 0).
    - **Actual Line:** Đường thực tế.
- **Scope Creep Detection:** Nếu có Task mới được thêm vào giữa Sprint, biểu đồ Burn-up phải hiển thị sự gia tăng của đường Scope, làm nổi bật sự thay đổi phạm vi.
#### AC 2 - Velocity Chart
- Hiển thị biểu đồ cột so sánh `Commitment` (Cam kết ban đầu) và `Completed` (Hoàn thành thực tế) qua các Sprint lịch sử.
- Tự động tính toán **Average Velocity** (Vận tốc trung bình) của 3 Sprint gần nhất để hỗ trợ lập kế hoạch.
## 2.2. Feature: Resource Utilization Heatmap (Bản đồ Nhiệt Nguồn lực)
### User Story 11.2
Là một Resource Manager, Tôi muốn nhìn thấy mức độ tải việc của từng thành viên qua biểu đồ nhiệt (Heatmap), Để phát hiện ai đang bị quá tải (Overload) hoặc rảnh rỗi (Underutilized) nhằm điều phối lại nguồn lực.
### Acceptance Criteria ( #AC)
#### AC 1 - Capacity Visualization
- **Logic:** So sánh `Assigned Hours` với `Working Capacity` (ví dụ: 8h/ngày).
- **Color Coding:**
    - **Green:** 70-90% Capacity (Tối ưu).
    - **Red:** > 100% Capacity (Quá tải).
    - **Grey:** < 50% Capacity (Rảnh rỗi).
#### AC 2 - Drill-down Capability
- Cho phép click vào một ô màu trên Heatmap để xem danh sách chi tiết các Task đang chiếm dụng thời gian của nhân sự đó trong ngày.
## 2.3. Feature: Time Tracking & Timesheets (Theo dõi Thời gian & Bảng chấm công)
### User Story 11.3
Là một Freelancer/Nhân viên, Tôi muốn ghi lại thời gian thực tế tôi dành cho mỗi đầu việc và phân loại chúng, Để làm cơ sở tính lương hoặc xuất hóa đơn cho khách hàng.
### Acceptance Criteria ( #AC)

#### AC 1 - Timer & Manual Entry
- **Timer:** Widget bấm giờ (Start/Stop) chạy nổi trên giao diện, tự động tính toán thời gian `hh:mm:ss`.
- **Manual:** Cho phép nhập tay hoặc điều chỉnh thời gian nếu quên bấm giờ (cần ghi log chỉnh sửa).
#### AC 2 - Billable vs. Non-billable
- Mỗi bản ghi thời gian (Time Entry) phải có cờ (Flag) `is_billable`.
- **Default:** Kế thừa từ cài đặt của Dự án. Nếu Dự án là "Internal", mặc định là Non-billable.
#### AC 3 - Timesheet Approval Workflow
- Cuối tuần/tháng, nhân viên gửi Timesheet. PM nhận thông báo để "Approve" hoặc "Reject" (kèm lý do). Chỉ Timesheet đã duyệt mới được đẩy sang Module 13 để tính tiền.
## 2.4. Feature: Custom Report Builder (Trình tạo báo cáo tùy chỉnh)
### User Story 11.4
Là một Data Analyst, Tôi muốn tự thiết kế các báo cáo riêng dựa trên các trường dữ liệu tùy chỉnh (Custom Fields) mà không phụ thuộc vào các mẫu có sẵn, Để phục vụ nhu cầu báo cáo đặc thù của ban giám đốc.
### Acceptance Criteria ( #AC)
#### AC 1 - Drag & Drop Interface
- Cung cấp giao diện kéo thả để chọn:
    - **Dimensions (Trục phân tích):** Project, Assignee, Tag, Priority, Month.
    - **Metrics (Chỉ số đo lường):** Count of Tasks, Sum of Hours, Avg Cycle Time.
#### AC 2 - Filtering & Export
- Hỗ trợ bộ lọc nâng cao (SQL-like logic: AND, OR).
- Cho phép xuất báo cáo ra định dạng `.pdf` (để in ấn) và `.csv/.xlsx` (để xử lý thêm).
# 3. Business Rules & Technical Constraints
## 3.1. Quy tắc Bảo mật Dữ liệu Báo cáo (Data Visibility)
- **Salary/Cost Privacy:** Các trường dữ liệu nhạy cảm như `Hourly Rate` (Mức lương giờ) hoặc `Total Cost` chỉ hiển thị với vai trò **Owner** và **Admin**.
- Member bình thường chỉ xem được số giờ (`Total Hours`) của bản thân và biểu đồ tiến độ chung của dự án, không xem được Timesheet chi tiết của đồng nghiệp (trừ khi được ủy quyền).
## 3.2. Quy tắc Làm tươi Dữ liệu (Data Freshness)
- Các báo cáo vận hành (Operational Reports) như Burn-down chart cần dữ liệu **Real-time** hoặc độ trễ thấp (< 1 phút).
- Các báo cáo phân tích xu hướng dài hạn (Trend Analysis) có thể sử dụng dữ liệu từ **Read Replica** hoặc **Data Warehouse** với độ trễ chấp nhận được (ví dụ: cập nhật sau mỗi 1 giờ) để giảm tải cho Database chính.
## 3.3. Quy tắc Ghi nhận Thời gian (Time Logging Rules)
- Không cho phép ghi nhận thời gian cho tương lai (Future Logging) vượt quá ngày hiện tại (trừ trường hợp đăng ký nghỉ phép - Leave Request).
- Tổng thời gian log trong một ngày không được vượt quá 24h (Hard Validation). Cảnh báo mềm (Soft Warning) nếu vượt quá 12h/ngày.
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Quản lý Giá trị Thu được (Earned Value Management - #EVM)
Module áp dụng chuẩn EVM để đo lường hiệu quả dự án khách quan:
- **Planned Value (PV):** Khối lượng công việc dự kiến hoàn thành.
- **Earned Value (EV):** Khối lượng công việc thực tế đã hoàn thành.
- Actual Cost (AC): Chi phí thực tế bỏ ra (dựa trên Time logs).
    -> Hệ thống tự động tính toán chỉ số CPI (Cost Performance Index) và SPI (Schedule Performance Index). Nếu $SPI < 1$, dự án đang chậm tiến độ.
## 4.2. Định luật Little & Flow Metrics (Kanban Analytics)
Áp dụng cho các báo cáo luồng công việc:
- **Cycle Time:** Thời gian từ khi bắt đầu (In-Progress) đến khi hoàn thành (Done).
- **Lead Time:** Thời gian từ khi yêu cầu (New) đến khi hoàn thành (Done).
- Throughput: Số lượng task hoàn thành trên một đơn vị thời gian.
    Việc theo dõi Cycle Time giúp phát hiện các điểm nghẽn (Bottlenecks) trong quy trình sản xuất.
## 4.3. Nguyên lý Pareto (Quy tắc 80/20)
Áp dụng trong báo cáo lỗi (Bug Reporting):
- Biểu đồ Pareto giúp nhận diện "20% nguyên nhân gây ra 80% lỗi".
- Hệ thống tự động nhóm các lỗi theo `Category` hoặc `Module` và sắp xếp giảm dần, giúp team tập trung xử lý các vùng lỗi trọng yếu trước.