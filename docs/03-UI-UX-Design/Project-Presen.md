Quy tắc tuân thủ:
- Governance Mode: Simple & Strict
- Project Visibility: Public & Private
- Project Roles:

# Các nhóm giao diện
## 1. Nhóm giao diện theo Chế độ Quản trị
> Governance Mode

| Governance Mode | Đối tượng thụ hưởng                  | Đặc điểm                                                                                  | Thành phần UI                                                                                                                                                 |
| --------------- | ------------------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *Simple Mode*     | Dành cho dự án nhỏ / Agile           | Tối giản, tùy chọn ẩn các tính năng rườm rà (khác với các tính năng đặc thù project-mode) | Cho phép sửa ngày trực tiếp trên Gantt, không có quy trình duyệt PCR, không hiển thị các nút "Request Approval" hay "Baselien Version"                        |
| *Strict Mode*     | Dành cho dự án Enterprise / Hợp đồng | Kiểm soát chặt chẽ, kích hợp toàn bộ hàng rào bảo vệ.                                     | Hiển thị danh sách các phiên bản baseline (version#), bắt buộc nhập lý do (Change Context) khi sửa lịch trình, tích hợp luồng phê duyệt PCR (Change Request). |
## 2. Nhóm Giao diện theo Vai trò Người ddùng
> Role-based View

Tùy từng vai trò trong dự án (Project Role), người dùng sẽ thấy các bộ công cụ khác nhau:

| **Views (Đối tượng thụ hưởng)**  | **Permission**                            | **Tính năng đặc biệt**                                                                                                                                                                     |
| -------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| *Project Manager / Owner*        | Toàn quyền                                | Menu cấu hình dự án (Setting), quản lý thành viên, phê duyệt #PCR, thiết lập ngân sách/ chi phí nhân sự (Financial data), và thực hiện chuyển giao quyền sở hữu (Ownership Transfer)..     |
| *Planner*                        | Chỉnh sửa kế hoạch nhưng hạn chế quản trị | Tập trung vào biểu đồ Gantt, chạy mô phỏng (Similation Mode), quản lý Baseline và Dependency. Không thấy dữ liệu về tiền bạc (Hourly Rate)                                                 |
| *Member*                         | Tập trung vào tác vụ                      | Giao diện tối ưu cho việc cập nhật trạng thái Task, log-time (Timesheet) và thảo luận. Bị chặn chỉnh sửa Gantt hoặc chuyển trạng thái dự án hoặc các cấu hình làm thay đổi tổng thể dự án. |
| *Viewer / Stakeholder / Auditor* | Chỉ đọc                                   | Chỉ xem báo cáo, tiến độ và tài liệu. Không có các nút tùy chỉnh. Auditor có thể xem Nhật ký hoạt động (Audit Log).                                                                        |
## 3. Nhóm Giao diện theo Trạng thái Vòng đời
>Lifecycle States

Giao diện sẽ thay đổi dựa trên trạng thái hiện tại của dự án để ngăn chặn sai sót:

| Views    | States                | Description                                                                                                                                                 |
| -------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Active   | IN_PROGRESS, PLANNING | Đầy đủ các tính năng tương tác ghi/đọc                                                                                                                      |
| Terminal | DONE, CANCELLED       | - Hệ thống khóa các quyền chỉnh sửa thông tin dự án và Task<br>- Hiển thị Wizad "Project Closure" (đối với PM) để thu thập Lessons Learned và đánh giá KPI. |
| Archived | Lưu trữ               | Chế độ "Cold Storage", ẩn mọi tương tác ghi, chỉ cho phép xem hoặc xuất dữ liệu (Export)                                                                    |
## 4. Nhóm Giao diện Đặc thù

> Special Purpose Views

| Views           | Description                                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Simulation Mode | - Chế độ hộp cát để thử nghiệm các kịch bản "What-if"<br>- Giao diện thay đổi tông màu để phân biệt với dữ liệu thật.                                          |
| Private Project | - Dành riêng cho các dự án có tính bảo mật cao.<br>- Chỉ hiển thị với thành viên được mời. Đối với Workspace Owner, nếu truy cập sẽ có cảnh bảo "Audit Access" |
## 5. Nhóm Giao diện Quản trị Danh mục
> Portfolio & Program View

Nhóm giao diện dành cho cấp quản lý cao hơn Project Manager để theo dõi nhiều dự án cùng lúc.

| Views                      | Description                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| Portfolio Dashboard        | Gom nhóm ác dự án theo Category hoặc Portfolio Tag                                           |
| Health Traffic Light       | Hiển thị danh sách dự án dưới dạng traffic-light dựa trên chỉ số Schedule, Resoure và Budget |
| Cross-Project Dependencies | hiển thị các mmốiquan hệ phụ thuộc giữa các dự án khác nhau trong cùng một Portfolio         |
## 6. Nhóm Giao diện Kiểm soát và Phê duyệt
> Các giao này xuất hiện tại các "điểm chạm" quy trình để đảm bảo tuân thủ, đặc biệt trong Strict Mode

| Views                           | Description                                                                                                                                                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Change Request (PCR) Management | - Màn hình tạo yêu cầu thay đổi (Scope, Schedule, Cost)<br>- Bảng phân tích tác động (Impact Analysis) so sánh giữa kế hoạch cũ và đề xuất mới.<br>- Màn hình duyệt/ từ chối dành cho Steering Comittee hoặc Admin |
| Status Transition Gates         | - Modal kiểm tra "Definition of Done" ( #DoD) khi chuển sang trạng thái DONE, liệt kê các Task chưa xong và yêu cầu xử lý.<br>- Giao diện phê duyệt kế hoạch (Planning Approval) trước khi chuyển sang IN_PROGRESS |
## 7. Nhóm Giao diện Cá nhân hóa và Hỗ trợ
> Nhóm giao diện phục vụ trải nghiệm người dùng cuối và các tình huống ngoại lệ

| Views                   | Description                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Personal Workspace      | Hiển thị các Task từ tất cả các dự án mà người dùng tham gia, được sắp xếp theo độ ưu tiên toàn cục                            |
| Simulatio Sandbox       | Màn hình so sánh "Diff" giữa kịch bản mô phỏng và dự án thực tế về ngày kết thúc, chi phí và rủi ro đường găng (Critical Path) |
| Lessons Learned Library | Nơi lưu trữ và tra cứu các bài học kinh nghiệm từ các dự án đã đóng để áp dụng cho dự án mới                                   |
# 8. Nhóm Giao diện xử lý "Dự án mồ côi"
> Orphan Project Handling

Giao diện quản trị đặc thù dành cho Workspace Admin
- Giao diện Transfer Ownership Wizad: Xuất hiện khi một PM nghỉ việc hoặc bị Deactive tài khoản, yêu cầu Admin chuyển quyền sở hữu dự án cho người khác trước khi xóa tài khoản cũ.

# Ma trận Giao diện cần triển khai:
|**Nhóm Giao diện**|**Loại hình / Vai trò**|**Key UI Components**|
|---|---|---|
|**Theo Mode**|Simple vs. Strict|PCR Panel, Baseline History, Freeze Zone overlays.|
|**Theo Role**|PM, Planner, Member, Viewer|Settings tab, Financial reports, Task Edit constraints.|
|**Theo Lifecycle**|Active, Done, Archived|Closure Wizard, Read-only banners, Restore button.|
|**Đặc thù**|Simulation, Personal/Private|Sandbox Watermark, Impact Analysis Diff, Privacy alerts.|