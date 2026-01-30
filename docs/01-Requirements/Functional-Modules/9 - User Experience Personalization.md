Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---
# 1. Business Overview

Trong kỷ nguyên phần mềm hiện đại, "One size fits all" (Một giao diện cho tất cả) không còn là cách tiếp cận phù hợp. Mỗi người dùng có thói quen làm việc (Mental Model), điều kiện môi trường (Context) và giới hạn thể chất khác nhau.
Module **User Experience Personalization** của PronaFlow không đơn thuần là việc thay đổi màu sắc trang trí. Mục tiêu cốt lõi của nó là **Tối ưu hóa Hiệu suất Cá nhân** thông qua việc:
1. **Giảm tải Nhận thức (Cognitive Load Reduction):** Cho phép người dùng ẩn bớt các tính năng/thông tin không cần thiết, giúp họ tập trung vào tác vụ chính.
2. **Tăng khả năng Tiếp cận (Accessibility):** Hỗ trợ người dùng có thị lực kém hoặc làm việc trong môi trường thiếu sáng.
3. **Bản địa hóa (Localization):** Xóa bỏ rào cản ngôn ngữ và văn hóa (Định dạng ngày tháng, tiền tệ).
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Internationalization (i18n) & Localization (l10n)
### User Story 9.1
Là một Người dùng đa quốc gia, Tôi muốn hệ thống hiển thị ngôn ngữ và định dạng ngày tháng quen thuộc với văn hóa của tôi, Để tôi có thể hiểu và xử lý thông tin chính xác mà không cần "dịch" trong đầu.
### Acceptance Criteria ( #AC)
#### AC 1 - Language Switching (Chuyển đổi ngôn ngữ)
- **Support:** Hỗ trợ tối thiểu 2 ngôn ngữ: Tiếng Anh (en-US) và Tiếng Việt (vi-VN).
- **Mechanism:** Việc chuyển đổi ngôn ngữ diễn ra tức thì (Hot-swap) mà không yêu cầu tải lại trang (F5), nhờ vào thư viện `i18next`.
- **Fallback:** Nếu một từ khóa chưa được dịch sang Tiếng Việt, hệ thống tự động hiển thị Tiếng Anh thay vì mã lỗi.
#### AC 2 - Format Localization (Định dạng cục bộ)
- **Date/Time:**
    - VN: `DD/MM/YYYY` (28/12/2025).
    - US: `MM/DD/YYYY` (12/28/2025).
- **Number/Currency:**
    - VN: `1.000.000 ₫` (Dấu chấm phân cách hàng nghìn).
    - US: `1,000,000 $` (Dấu phẩy phân cách hàng nghìn).
## 2.2. Feature: Theme & Appearance (Giao diện & Hiển thị)
### User Story 9.2
Là một Lập trình viên thường làm việc vào ban đêm, Tôi muốn chuyển giao diện sang chế độ tối (Dark Mode), Để giảm mỏi mắt (Eye Strain) và tiết kiệm pin thiết bị.
### Acceptance Criteria (#AC)
#### AC 1 - Theme Modes
- Hỗ trợ 3 chế độ:
    1. **Light:** Giao diện sáng mặc định.
    2. **Dark:** Giao diện tối (Màu nền `#121212`, Text trắng).
    3. **System Sync:** Tự động chuyển đổi dựa trên cài đặt của Hệ điều hành (OS Settings).
#### AC 2 - Contrast Ratio (Tỷ lệ tương phản)
- Tuân thủ tiêu chuẩn **WCAG 2.1 Level AA**: Đảm bảo tỷ lệ tương phản giữa văn bản và nền tối thiểu là **4.5:1** cho văn bản thường, giúp nội dung luôn dễ đọc ở mọi chế độ.
## 2.3. Feature: Customizable Dashboard (Bảng điều khiển Tùy biến)
### User Story 9.3
Là một Project Manager, Tôi muốn sắp xếp các Widget trên màn hình chính theo thứ tự ưu tiên của riêng mình, Để tôi có thể nhìn thấy các chỉ số quan trọng (KPIs) ngay khi đăng nhập.
### Acceptance Criteria ( #AC)
#### AC 1 - Widget Library
- Cung cấp kho Widget (My Tasks, Project Progress, Calendar, Recent Activities).
- Người dùng có thể: Thêm mới, Xóa bỏ (Hide), hoặc Thay đổi kích thước (Resize) các Widget.
#### AC 2 - Drag & Drop Layout
- Cho phép kéo thả để sắp xếp lại vị trí các Widget (sử dụng lưới Grid Layout).
- **Persistence:** Cấu hình bố cục (`layout_config`) phải được lưu vào Database. Khi người dùng đăng nhập trên thiết bị khác, bố cục này được đồng bộ về.
## 2.4. Feature: Workspace Layout Optimization (Tối ưu hóa Bố cục)

### User Story 9.4

Là một Power User cần không gian rộng để xem biểu đồ Gantt hoặc bảng Kanban lớn, Tôi muốn thu gọn thanh điều hướng (Sidebar) hoặc các panel phụ, Để tối đa hóa diện tích làm việc (Screen Real Estate).
### Acceptance Criteria ( #AC)
#### AC 1 - Collapsible Sidebar (Sidebar thu gọn)
- **Interaction:** Cung cấp nút Toggle (`<<`) và phím tắt (VD: `Ctrl/Cmd + B`) để đóng/mở Sidebar.
- **Mini-mode:** Khi thu gọn, Sidebar hiển thị dưới dạng icon-only (chỉ biểu tượng), hiển thị Tooltip khi hover để người dùng vẫn định vị được chức năng.
- **Response:** Nội dung chính (Main Content) phải tự động tính toán lại chiều rộng (Reflow) ngay lập tức, không để lại khoảng trắng thừa.
#### AC 2 - Information Density (Mật độ thông tin)
- Cho phép người dùng chọn giữa 2 chế độ hiển thị dữ liệu (áp dụng cho Task List và Table View).
    1. **Comfortable (Mặc định):** Padding rộng (12px-16px), phù hợp cho việc đọc lướt và thao tác cảm ứng.
    2. **Compact (Chật chội):** Padding hẹp (4px-8px), giảm kích thước font chữ tiêu đề.
    - _Lý do:_ Phù hợp cho Data Analyst hoặc Manager cần nhìn thấy nhiều dòng dữ liệu nhất có thể trên một màn hình mà không cần cuộn trang.
## 2.5. Feature: Typographic Accessibility (Tùy biến Typography)

### User Story 9.5

Là một người dùng mắc chứng khó đọc (Dyslexia) hoặc suy giảm thị lực tuổi già (Presbyopia), Tôi muốn điều chỉnh loại font và kích cỡ chữ, Để tăng khả năng đọc hiểu văn bản (Legibility).
### Acceptance Criteria ( #AC)
#### AC 1 - Global Font Size Scaling (Tỷ lệ Font chữ)
- **Mechanism:** Không set cứng `px` cho từng phần tử. Sử dụng đơn vị tương đối `rem` cho toàn bộ hệ thống UI.
- **Setting:** Người dùng điều chỉnh thanh trượt "Base Font Size":
    - Small (12px)
    - Medium (14px - Default standard)
    - Large (16px)
    - Extra Large (18px)
- **Impact:** Toàn bộ Button, Input, Text phải scale tỷ lệ thuận theo Base Font Size này.
#### AC 2 - Font Family Customization
- Cung cấp tùy chọn thay đổi Font chữ hệ thống:
    1. **System Default:** San Francisco (Mac) / Segoe UI (Win) - Tối ưu tốc độ tải.
    2. **Dyslexic Friendly:** Tích hợp font `OpenDyslexic` hoặc các font sans-serif có độ mở (aperture) lớn, khoảng cách ký tự rộng để hỗ trợ người mắc chứng khó đọc.
    3. **Monospace:** Dành cho Developer muốn giao diện giống IDE code
## 2.6. Feature: Notification Granularity (Kiểm soát Sự gián đoạn)
### User Story 9.6
Là một Lập trình viên cần sự tập trung cao độ (Deep Work), Tôi muốn tùy chỉnh chi tiết các loại thông báo và kênh nhận tin, Để tránh bị xao nhãng bởi các luồng thông tin không khẩn cấp (Notification Fatigue).
### Acceptance Criteria ( #AC)
#### AC 1 - Multi-Channel Routing (Định tuyến Đa kênh)
- **Matrix Configuration:** Người dùng có thể bật/tắt thông báo cho từng sự kiện cụ thể trên 3 kênh: **In-app**, **Email**, và **Browser Push**.
    - _Ví dụ:_ "Khi tôi được tag (@mention)" -> Bật cả 3 kênh.
    - _Ví dụ:_ "Khi task chuyển trạng thái" -> Chỉ bật In-app, tắt Email.
#### AC 2 - Do Not Disturb Schedule (Lịch Không làm phiền)
- **Automation:** Cho phép thiết lập khung giờ "Focus Time" (ví dụ: 08:00 - 10:00).
- **Behavior:** Trong khung giờ này, hệ thống chặn (suppress) toàn bộ thông báo Push và âm thanh, chỉ lưu vào "Notification Center" để xem lại sau.
- **Exception:** Cho phép thiết lập ngoại lệ cho các thông báo "Urgent" hoặc từ "Project Manager".
## 2.7. Feature: Keyboard Shortcuts & Power Usage (Phím tắt & Thao tác Nhanh)
### User Story 9.7
Là một Power User, Tôi muốn thực hiện các thao tác thường gặp (Tạo task, Gán người, Tìm kiếm) hoàn toàn bằng bàn phím, Để duy trì dòng chảy công việc (Flow State) mà không cần nhấc tay khỏi bàn phím để dùng chuột.
### Acceptance Criteria ( #AC)
#### AC 1 - Global Shortcuts Map
- Hỗ trợ phím tắt toàn cục:
    - `Cmd/Ctrl + K`: Mở thanh Command Palette (Tìm kiếm nhanh chức năng).
    - `C`: Mở modal tạo Task mới (Create).
    - `?`: Hiển thị bảng tra cứu phím tắt (Cheatsheet).
#### AC 2 - Contextual Navigation (Điều hướng Ngữ cảnh)
- Trong giao diện Kanban/List:
    - Sử dụng phím mũi tên hoặc `J/K` (Vim-style) để di chuyển vùng chọn giữa các Project/Task.
    - `Space`: Mở xem chi tiết Project/Task đang chọn (Preview).
## 2.8. Feature: Color Vision Deficiency Support (Hỗ trợ Khiếm khuyết Màu sắc)
### User Story 9.8
Là một người dùng bị mù màu đỏ-xanh (Deuteranopia), Tôi muốn hệ thống tự động điều chỉnh bảng màu của các biểu đồ và trạng thái, Để tôi có thể phân biệt rõ ràng giữa "Hoàn thành" (thường là Xanh) và "Lỗi/Trễ hạn" (thường là Đỏ).
### Acceptance Criteria (#AC)
#### AC 1 - Daltonization Filters (Bộ lọc Dalton)
- Cung cấp tùy chọn "Color Blindness Mode" trong cài đặt Accessibility:
    1. **Deuteranopia/Protanopia (Red-Green):** Chuyển mã màu trạng thái từ Xanh/Đỏ sang Xanh lam/Cam nghệ.
    2. **Tritanopia (Blue-Yellow):** Điều chỉnh sang tông màu Hồng/Xanh lơ (Cyan).
- **Chart Adaptation:** Tự động thay thế việc chỉ dùng màu sắc bằng việc kết hợp **Màu sắc + Họa tiết (Pattern)** (ví dụ: gạch chéo, chấm bi) trên các biểu đồ tròn/cột.
# 3. Business Rules & Technical Constraints
## 3.1. Quy tắc Lưu trữ Cấu hình (Configuration Persistence)
Hệ thống áp dụng cơ chế lưu trữ 2 lớp (Dual-Layer Persistence) để đảm bảo trải nghiệm liền mạch:
1. **Local Storage (Client-side):** Lưu cài đặt `Theme` và `Language` để áp dụng ngay lập tức khi ứng dụng vừa khởi động (trước khi gọi API). Tránh hiện tượng "Flash of Wrong Theme".
2. **Database (Server-side):** Đồng bộ các cài đặt này vào `user_settings` table. Giúp duy trì trải nghiệm đồng nhất khi người dùng chuyển đổi thiết bị (Roaming Profile).
## 3.2. Quy tắc Mặc định (Default Behavior)
- Khi người dùng truy cập lần đầu (Guest/New User):
    - **Ngôn ngữ:** Tự động phát hiện dựa trên `navigator.language` của trình duyệt.
    - **Giao diện:** Tự động phát hiện dựa trên `prefers-color-scheme` media query.
## 3.3. Quy tắc Ràng buộc UI (UI Constraints)
- **Minimum Viable Width:** Dù người dùng phóng to cỡ chữ đến đâu, hệ thống phải đảm bảo các nút bấm chức năng quan trọng (Save, Cancel, Close) không bị đẩy ra khỏi màn hình (Overflow). Cần sử dụng `text-overflow: ellipsis` kết hợp Tooltip cho các đoạn văn bản bị cắt ngắn.

## 3.4. Quy tắc Ưu tiên Thiết lập (Configuration Precedence)
Khi có xung đột về cài đặt hiển thị, hệ thống áp dụng thứ tự ưu tiên sau (từ cao xuống thấp):
1. **User Preference:** Cài đặt cá nhân của người dùng (trong module này).
2. **Workspace Policy:** Cài đặt bắt buộc do Admin quy định (ví dụ: bắt buộc bật 2FA, bắt buộc nhận email thông báo Deadline).
3. **System Default:** Cài đặt mặc định của hệ thống PronaFlow. _Lý do:_ Đảm bảo tính cá nhân hóa nhưng không vi phạm các quy tắc quản trị/bảo mật chung của tổ chức.
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Định luật Hick (Hick's Law)

> _"Thời gian cần thiết để đưa ra quyết định tăng theo số lượng và độ phức tạp của các lựa chọn."_

Áp dụng vào **Customizable Dashboard**: Bằng cách cho phép người dùng ẩn đi các Widget không cần thiết, chúng ta giảm số lượng tác nhân kích thích (Stimuli), giúp người dùng ra quyết định nhanh hơn và tập trung hơn vào công việc chính.
## 4.2. Thuyết Tải Nhận thức (Cognitive Load Theory - John Sweller)
- **Extraneous Load (Tải ngoại lai):** Là những thông tin thừa thãi, gây nhiễu.
- **Giải pháp:** Tính năng Personalization giúp loại bỏ _Extraneous Load_ (ví dụ: một Dev không cần xem biểu đồ chi phí dự án). Điều này giải phóng tài nguyên não bộ để tập trung vào **Germane Load** (Tải trọng thiết yếu - việc xử lý logic công việc).
## 4.3. Tiêu chuẩn Tiếp cận Web (Web Content Accessibility Guidelines - WCAG)
Module này được xây dựng để đáp ứng các tiêu chuẩn đạo đức và pháp lý trong thiết kế phần mềm:
- **Perceivable (Có thể nhận biết):** Dark Mode và High Contrast giúp người khiếm thị màu hoặc nhạy cảm ánh sáng vẫn sử dụng được phần mềm.
- **Operable (Có thể điều hướng):** Hỗ trợ điều hướng bằng bàn phím (Keyboard Navigation) cho toàn bộ các menu tùy chỉnh.
## 4.4. Định luật Fitts (Fitts's Law)

> _"Thời gian cần thiết để di chuyển nhanh tới mục tiêu là hàm số của khoảng cách tới mục tiêu và kích thước của mục tiêu đó."_

- **Áp dụng:** Tính năng **Collapsible Sidebar** giúp mở rộng không gian làm việc, làm cho các thẻ Kanban (mục tiêu thao tác) trở nên to hơn hoặc hiển thị được nhiều hơn, giảm quãng đường chuột người dùng phải di chuyển khi thao tác kéo thả.
## 4.5. Data-Ink Ratio (Tỷ lệ Dữ liệu/Mực in - Edward Tufte)
- **Nguyên lý:** Một giao diện tốt là giao diện loại bỏ tối đa các yếu tố trang trí không mang lại thông tin (non-data-ink).
- **Áp dụng:** Chế độ **Compact Mode** (AC 2 của Feature 9.4) loại bỏ các khoảng trắng (whitespace) thừa thãi, tối ưu hóa tỷ lệ hiển thị thông tin nghiệp vụ trên mỗi pixel màn hình, phục vụ nhóm người dùng chuyên gia (Expert Users).
## 4.6. Khoa học về Sự gián đoạn (Interruption Science)
Các nghiên cứu (ví dụ: _Ogan, 2018_) chỉ ra rằng nhân viên văn phòng mất trung bình **23 phút 15 giây** để quay lại guồng công việc sau khi bị gián đoạn bởi một thông báo không liên quan.
- **Áp dụng:** Tính năng **Notification Granularity** (AC 9.6) và **Do Not Disturb** là biện pháp kỹ thuật trực tiếp để bảo vệ sự tập trung của người dùng, giảm thiểu _Context Switching Cost_ (Chi phí chuyển đổi ngữ cảnh).
## 4.7. Định luật Luyện tập (The Power Law of Practice)

> _"Logarithm của thời gian thực hiện một tác vụ giảm tuyến tính với logarithm của số lần luyện tập."_

- **Áp dụng:** Đối với người dùng lâu năm (Expert), thời gian thao tác bằng chuột sẽ chạm ngưỡng giới hạn vật lý. Tính năng **Keyboard Shortcuts** (AC 9.7) giúp phá vỡ giới hạn này, cho phép tốc độ thao tác tiệm cận với tốc độ tư duy, tối ưu hóa hiệu suất làm việc ở giai đoạn "Thành thạo" (Mastery Stage).
## 4.8. Thiết kế Bao trùm (Inclusive Design)
Khác với thiết kế phổ quát (Universal Design), Thiết kế bao trùm thừa nhận sự đa dạng của con người.
- **Áp dụng:** Việc hỗ trợ chế độ mù màu (AC 9.8) không chỉ là tính năng y tế, mà là yêu cầu bắt buộc để đảm bảo sự công bằng trong việc tiếp cận thông tin (Information Equity). Khoảng 8% nam giới bị mù màu, đây là một tập người dùng đáng kể trong môi trường doanh nghiệp không thể bị bỏ rơi.