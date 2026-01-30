Project**: PronaFlow
**Version**: 1.0
**State**: Draft
***Last updated:** Dec 31, 2025*

---
# 1. Business Overview
Trong mô hình Product-Led Growth (PLG), sản phẩm phải tự bán chính nó. Tuy nhiên, với một hệ thống phức tạp như PronaFlow (quản lý dự án kết hợp AI), người dùng mới thường bị choáng ngợp (Overwhelmed) bởi quá nhiều tính năng. Nếu không có quy trình dẫn nhập tốt, tỷ lệ rớt (Drop-off rate) sau lần đăng nhập đầu tiên sẽ rất cao.
Phân hệ **User Onboarding & Adoption** được thiết kế để giải quyết bài toán "Time-to-Value" (Thời gian để nhận được giá trị). Mục tiêu là rút ngắn khoảng cách từ khi người dùng đăng ký đến khi họ trải nghiệm được khoảnh khắc "Aha!" (Aha Moment) đầu tiên (ví dụ: tạo thành công một dự án và thấy AI gợi ý nhân sự).
Cách tiếp cận của PronaFlow là **"Learning by Doing"** (Học đi đôi với hành), thay vì bắt người dùng xem hết video hướng dẫn rồi mới làm.
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Role-Based Onboarding Flow (Luồng Dẫn nhập theo Vai trò)
### User Story 16.1
Là một Người dùng mới đăng ký, Tôi muốn hệ thống hỏi về vai trò và mục tiêu của tôi (ví dụ: "Tôi là PM muốn quản lý team 10 người"), Để giao diện và hướng dẫn được tùy chỉnh phù hợp ngay từ đầu.
### Acceptance Criteria ( #AC)
#### AC 1 - Welcome Survey
- Ngay sau khi đăng ký, hiển thị màn hình chào mừng (Welcome Screen) với 2-3 câu hỏi trắc nghiệm:
 - _Role:_ Project Manager / Developer / Stakeholder.
 - _Goal:_ Quản lý Task / Theo dõi tiến độ / Báo cáo.
 - _Experience:_ Đã dùng Jira/Trello chưa?
#### AC 2 - Persona Mapping
- Hệ thống lưu câu trả lời vào `User Profile` và tự động cấu hình:
 - **Developer:** Ẩn các menu Billing/Settings, highlight tính năng "My Tasks" và "Git Integration".
 - **Manager:** Highlight tính năng "Create Project" và "Dashboard Reports".
## 2.2. Feature: Interactive Product Tour (Tour Sản phẩm Tương tác)
### User Story 16.2
Là một Người dùng lần đầu vào màn hình Kanban, Tôi muốn có một hướng dẫn từng bước chỉ cho tôi cách tạo cột và kéo thả thẻ, Để tôi nắm bắt cách sử dụng cơ bản mà không cần mò mẫm.
### Acceptance Criteria ( #AC)
#### AC 1 - Highlight & Overlay
- Sử dụng thư viện (như `React Joyride` hoặc `Driver.js`) để làm tối màn hình nền và làm nổi bật (Highlight) phần tử UI cần thao tác.
- Hiển thị Tooltip hướng dẫn: "Nhấn vào đây để thêm Task mới".
#### AC 2 - Interaction Requirement
- Tour không chỉ là Slide tĩnh. Người dùng **phải thực hiện hành động** (Click nút, Nhập text) thì mới chuyển sang bước tiếp theo.
- Có nút "Skip Tour" cho người dùng đã thành thạo.
## 2.3. Feature: Onboarding Checklist (Danh sách Kiểm tra Dẫn nhập)
### User Story 16.3
Là một Người dùng mới, Tôi muốn nhìn thấy một thanh tiến độ hiển thị các bước cần hoàn thành để thiết lập tài khoản (ví dụ: Upload Avatar, Tạo dự án đầu tiên), Để tôi có động lực hoàn tất hồ sơ.
### Acceptance Criteria ( #AC)
#### AC 1 - Gamification Progress
- Widget "Getting Started" hiển thị ở góc dưới màn hình hoặc Dashboard.
- Danh sách nhiệm vụ:
 1. Tạo Workspace (Done).
 2. Mời 1 thành viên (Pending).
 3. Tạo 1 Task (Pending).
- Thanh tiến độ tăng dần (33% -> 66% -> 100%).
#### AC 2 - Reward (Phần thưởng)
- Khi hoàn thành 100% Checklist, hệ thống hiển thị hiệu ứng chúc mừng (Confetti) và tặng một phần thưởng nhỏ (ví dụ: +7 ngày dùng thử bản Pro).
## 2.4. Feature: Contextual Feature Discovery (Khám phá Tính năng Ngữ cảnh)
### User Story 16.4
Là một Người dùng cũ, khi hệ thống cập nhật tính năng mới "AI Prediction", Tôi muốn nhìn thấy một chấm xanh (Beacon) thu hút sự chú ý tại nút đó, Để tôi biết và thử nghiệm tính năng mới.
### Acceptance Criteria ( #AC)
#### AC 1 - Hotspots (Điểm nóng)
- Hiển thị một chấm tròn nhấp nháy (Pulsing Dot) cạnh UI element mới.
- Khi Hover chuột vào, mở ra Tooltip giải thích ngắn gọn: "Mới! Bấm vào đây để AI dự đoán thời gian làm việc".
#### AC 2 - Dismissal Logic
- Nếu người dùng đã click vào tính năng đó 1 lần, Hotspot phải tự động biến mất vĩnh viễn (One-time Discovery).
# 3. Business Rules & Technical Constraints
## 3.1. Quy tắc "Không làm phiền" (Anti-Annoyance Rule)
- **Frequency Cap:** Không hiển thị quá 1 Product Tour trong một phiên làm việc.
- **Persistence:** Trạng thái của Onboarding (Step hiện tại, đã hoàn thành hay chưa) phải được lưu trong Database (bảng `user_onboarding_status`), không chỉ lưu ở LocalStorage. Điều này đảm bảo nếu user đổi máy tính, họ không bị bắt làm lại từ đầu.
## 3.2. Quy tắc Bỏ qua (Skip Logic)
- Luôn luôn cung cấp tùy chọn "Skip" hoặc nút "X" rõ ràng trên mọi màn hình hướng dẫn. Không bao giờ ép buộc người dùng đi hết flow nếu họ không muốn (trừ các bước setup bắt buộc về kỹ thuật).
## 3.3. Hiệu năng UI
- Các thư viện hướng dẫn (Joyride/Driver) chỉ được tải (Lazy Load) khi cần thiết, không được làm chậm thời gian tải trang chính (Main Bundle Size).
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Hiệu ứng Zeigarnik (The Zeigarnik Effect)
Áp dụng vào **Onboarding Checklist**:
- Tâm lý học chứng minh con người thường nhớ và day dứt về các nhiệm vụ chưa hoàn thành hơn là các nhiệm vụ đã xong.
- Việc hiển thị thanh tiến độ "2/5 bước hoàn thành" thúc đẩy người dùng thực hiện nốt 3 bước còn lại để đạt trạng thái trọn vẹn (Closure).
## 4.2. Vùng phát triển gần (Zone of Proximal Development - Vygotsky)
Áp dụng vào **Interactive Tour**:
- Khái niệm "Scaffolding" (Giàn giáo): Hệ thống cung cấp sự hỗ trợ vừa đủ (Highlight, Tooltip) để người dùng thực hiện được tác vụ khó mà bình thường họ không tự làm được. Khi người dùng đã quen, "giàn giáo" này sẽ được tháo bỏ.
## 4.3. Mô hình Hook (Nir Eyal)
- **Trigger:** Email nhắc nhở hoặc Hotspot thông báo tính năng mới.
- **Action:** Người dùng click vào dùng thử.
- **Variable Reward:** Người dùng thấy AI dự đoán đúng (Aha Moment).
- **Investment:** Người dùng nhập thêm dữ liệu vào hệ thống, làm tăng khả năng quay lại lần sau.
