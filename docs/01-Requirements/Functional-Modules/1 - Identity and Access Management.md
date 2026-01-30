**Project**: PronaFlow 
**Version**: 1.1 
**State**: Draft 
_**Last updated:** Jan 04, 2026_

---
# 1. Business Overview
Phân hệ **Identity and Access Management (IAM)** đóng vai trò là tầng kiểm soát an ninh cốt lõi của hệ thống PronaFlow. Mục tiêu của phân hệ này là thiết lập và duy trì khuôn khổ bảo mật dựa trên mô hình **AAA** (Authentication - Authorization - Accounting/Auditing). Trong kiến trúc phần mềm SaaS (Software-as-a-Service), IAM đảm nhiệm chức năng định danh người dùng, xác thực quyền truy cập và đảm bảo tính toàn vẹn của phiên làm việc đối với tài nguyên dữ liệu của từng Tenant (Khách hàng/Tổ chức).
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Identity Lifecycle Management (Quản lý Vòng đời Định danh)
### User Story 1.1
Là một Người dùng mới, Tôi muốn đăng ký tài khoản và xác thực địa chỉ email, Để đảm bảo danh tính của tôi là duy nhất và an toàn trước khi tham gia vào các Workspace.
### Acceptance Criteria ( #AC)
#### AC 1 - Input Validation (Kiểm tra dữ liệu đầu vào)
- **Constraint:** Hệ thống phải kiểm tra định dạng dữ liệu trước khi xử lý:
 - `Email`: Phải đúng định dạng email tiêu chuẩn.
 - `Username`: Chỉ chứa chữ cái, số, gạch dưới; không chứa khoảng trắng; độ dài 3-30 ký tự.
 - `Password`: Phải đạt độ mạnh an toàn (Tối thiểu 12 ký tự, bao gồm chữ hoa, thường, số và ký tự đặc biệt).
#### AC 2 - Email Verification (Xác thực Email)
- **Flow:** Sau khi người dùng đăng ký, tài khoản được tạo ở trạng thái `PENDING` (Chờ kích hoạt).
- **System Behavior:** Hệ thống gửi một email chứa liên kết kích hoạt (có hiệu lực trong 24 giờ).
- **Result:** Khi người dùng truy cập liên kết, trạng thái tài khoản chuyển sang `ACTIVE`. Nếu liên kết hết hạn, người dùng phải yêu cầu gửi lại email kích hoạt.
### User Story 1.2
- Là một Người dùng, 
- Tôi muốn đăng nhập an toàn vào hệ thống và duy trì phiên làm việc trong một khoảng thời gian hợp lý, 
- Để không phải nhập lại mật khẩu liên tục gây gián đoạn công việc.
### Acceptance Criteria ( #AC)
#### AC 1 - Authentication Mechanism (Cơ chế xác thực)
- **Input:** Người dùng cung cấp thông tin đăng nhập (Email/Username và Password).
- **Output:** Nếu thông tin chính xác, hệ thống cấp quyền truy cập phiên làm việc.
#### AC 2 - Brute-force Protection (Chống tấn công dò mật khẩu)
- **Rule:** Hệ thống giới hạn số lần đăng nhập sai liên tiếp.
- **Logic:** Nếu nhập sai mật khẩu 5 lần trong vòng 10 phút, tài khoản sẽ bị tạm khóa chức năng đăng nhập trong 15 phút. Một thông báo cảnh báo bảo mật sẽ được gửi đến email của chủ tài khoản.
## 2.2. Feature: Access Control & Authorization (Kiểm soát Truy cập & Phân quyền)
### User Story 1.3
Là một Quản trị viên Workspace, Tôi muốn phân quyền cụ thể cho từng thành viên theo vai trò, Để đảm bảo mỗi người chỉ truy cập được những dữ liệu cần thiết cho công việc (Nguyên tắc đặc quyền tối thiểu).
### Acceptance Criteria ( #AC)
#### AC 1 - Hierarchical Roles (Vai trò phân cấp)
- Hệ thống hỗ trợ các vai trò tiêu chuẩn sau:
 - **Workspace Owner:** Toàn quyền quản lý tổ chức, thanh toán và dữ liệu.
 - **Workspace Admin:** Quản lý thành viên và dự án, không có quyền truy cập thông tin thanh toán.
 - **Member:** Có quyền xem và chỉnh sửa trên các dự án được gán.
 - **Guest:** Chỉ có quyền xem (Read-only) trên các tài nguyên được chia sẻ cụ thể.
#### AC 2 - Permission Enforcement (Thực thi quyền hạn)
- **Logic:** Khi người dùng thực hiện một hành động (Ví dụ: Xóa dự án), hệ thống phải kiểm tra vai trò của người dùng đó.
- **Result:** Nếu vai trò không đủ thẩm quyền, hệ thống từ chối yêu cầu và hiển thị thông báo "Bạn không có quyền thực hiện hành động này".
## 2.3. Feature: Password Recovery (Khôi phục Mật khẩu)
### User Story 1.4
Là một Người dùng quên mật khẩu, Tôi muốn thiết lập lại mật khẩu mới thông qua email xác nhận, Để lấy lại quyền truy cập tài khoản một cách an toàn.
### Acceptance Criteria (#AC)
#### AC 1 - Secure Reset Process
- **Security:** Hệ thống không gửi lại mật khẩu cũ qua email.
- **Mechanism:** Hệ thống gửi một liên kết đặt lại mật khẩu duy nhất qua email. Liên kết này chỉ có hiệu lực sử dụng một lần và hết hạn sau 15 phút.
#### AC 2 - Session Termination (Chấm dứt phiên)
- **Logic:** Ngay khi mật khẩu được thay đổi thành công, hệ thống phải tự động đăng xuất tài khoản này trên tất cả các thiết bị khác đang hoạt động để đảm bảo an toàn.
## 2.4. Feature: Multi-Factor Authentication (Xác thực Đa yếu tố - MFA)
### User Story 1.5
Là một Người dùng đề cao tính bảo mật, Tôi muốn kích hoạt xác thực 2 lớp (2FA) bằng ứng dụng điện thoại, Để bảo vệ tài khoản ngay cả khi mật khẩu bị lộ.
### Acceptance Criteria (#AC)
#### AC 1 - Activation Flow (Quy trình kích hoạt)
- **Standard:** Hỗ trợ các ứng dụng tạo mã OTP tiêu chuẩn (như Google Authenticator, Microsoft Authenticator).
- **Verification:** Người dùng phải nhập đúng mã 6 số từ ứng dụng để hoàn tất việc kích hoạt.
#### AC 2 - Login Requirement (Yêu cầu đăng nhập)
- **Logic:** Khi tài khoản đã bật 2FA, quy trình đăng nhập yêu cầu 2 bước:
 1. Nhập Mật khẩu chính xác.
 2. Nhập mã OTP từ thiết bị tin cậy.
#### AC 3 - Backup Recovery (Phương án dự phòng)
- Hệ thống cung cấp bộ 10 mã dự phòng (Backup Codes) khi kích hoạt 2FA. Người dùng có thể sử dụng mã này để đăng nhập khi mất điện thoại.
## 2.5. Feature: Session Management (Quản lý Phiên làm việc)
### User Story 1.6
Là một Người dùng, Tôi muốn xem danh sách các thiết bị đang đăng nhập tài khoản của mình và có quyền đăng xuất chúng từ xa, Để kiểm soát rủi ro truy cập trái phép.
### Acceptance Criteria (#AC)
#### AC 1 - Session Information Visibility (Hiển thị thông tin phiên)
- **Display:** Hệ thống liệt kê danh sách các phiên đang hoạt động với các thông tin định danh dễ hiểu cho người dùng:
 - **Tên thiết bị & Trình duyệt:** (Ví dụ: Chrome trên Windows 10, Safari trên iPhone 14).
 - **Vị trí địa lý ước tính:** (Ví dụ: Thành phố Hồ Chí Minh, Việt Nam).
 - **Thời gian hoạt động gần nhất:** (Ví dụ: Vừa truy cập, Hoạt động 2 giờ trước).
 - **Trạng thái:** Đánh dấu rõ "Phiên hiện tại" (Current Session).
#### AC 2 - Concurrent Session Limit (Giới hạn phiên đồng thời)
- **Business Rule:** Mỗi tài khoản người dùng chỉ được phép duy trì đăng nhập tối đa trên 5 thiết bị đồng thời.
- **Rotation Logic:** Khi người dùng đăng nhập trên thiết bị thứ 6, hệ thống tự động đăng xuất phiên làm việc cũ nhất (có thời gian hoạt động xa nhất) để nhường chỗ cho phiên mới.
#### AC 3 - Remote Revocation (Thu hồi quyền truy cập từ xa)
- **Action:** Người dùng nhấn nút "Đăng xuất" (Log out) trên một thiết bị cụ thể trong danh sách.
- **Result:**
 - Phiên làm việc trên thiết bị đó bị chấm dứt hiệu lực ngay lập tức.
 - Tại lần thao tác tiếp theo trên thiết bị bị đăng xuất, người dùng sẽ bị đưa trở về màn hình đăng nhập.
#### AC 4 - Impossible Travel Alert (Cảnh báo Di chuyển Bất thường)
- **Detection Logic:** Hệ thống phát hiện hai lần đăng nhập liên tiếp xảy ra ở hai vị trí địa lý cách xa nhau trong khoảng thời gian ngắn không khả thi về mặt vật lý (Ví dụ: Đăng nhập tại Hà Nội, 5 phút sau đăng nhập tại London).
- **System Action:**
 - Gửi email cảnh báo bảo mật khẩn cấp cho người dùng.
 - Yêu cầu xác thực lại (Re-authentication) đối với phiên đăng nhập đáng ngờ.
## 2.6. Feature: Social Authentication (Định danh Mạng xã hội)
### User Story 1.7
Là một Người dùng mới, Tôi muốn đăng nhập nhanh bằng tài khoản Google hoặc GitHub, Để tiết kiệm thời gian và giảm bớt việc phải ghi nhớ nhiều mật khẩu.
### Acceptance Criteria (#AC)
#### AC 1 - Authorization Flow (Luồng ủy quyền)
- **Protocol:** Sử dụng giao thức ủy quyền tiêu chuẩn (OAuth 2.0).
- **Permission:** Hệ thống chỉ yêu cầu quyền truy cập thông tin cơ bản (Tên, Email, Avatar) từ nhà cung cấp dịch vụ, không yêu cầu các quyền truy cập dữ liệu riêng tư khác.
#### AC 2 - Account Linking & Provisioning (Liên kết & Khởi tạo)
- **Case 1 (Tài khoản đã tồn tại):** Nếu email từ Google/GitHub trùng với email đã có trong hệ thống, tự động liên kết và đăng nhập.
- **Case 2 (Tài khoản mới):** Nếu email chưa tồn tại, hệ thống tự động khởi tạo tài khoản mới với trạng thái "Đã xác thực email" và bỏ qua bước xác minh email thủ công.
# 3. Business Rules & Compliance
## 3.1. Quy tắc Bảo mật Dữ liệu Xác thực
- **Password Storage:** Mật khẩu phải được mã hóa một chiều (Hashing) trước khi lưu trữ vào cơ sở dữ liệu. Tuyệt đối không lưu trữ mật khẩu dưới dạng văn bản có thể đọc được.
- **Sensitive Data:** Các mã xác thực (OTP, Reset Token) không được hiển thị trong log hệ thống hoặc phản hồi API.
## 3.2. Quy tắc Định danh (Identity Rules)
- **Uniqueness:** Địa chỉ Email và Username phải là duy nhất trên toàn hệ thống.
- **Email Verification Requirement:** Người dùng chưa xác thực email sẽ bị hạn chế quyền truy cập (chỉ xem được Dashboard cá nhân, không thể tạo Dự án hoặc tham gia Workspace).
## 3.3. Quy tắc Phiên làm việc (Session Rules)
- **Session Timeout:** Phiên làm việc sẽ tự động hết hạn nếu người dùng không có bất kỳ thao tác nào (Inactive) trong vòng 7 ngày (đối với tùy chọn "Ghi nhớ đăng nhập").
- **Audit Trail:** Mọi hành động liên quan đến định danh (Đăng nhập, Đổi mật khẩu, Bật/Tắt 2FA) đều phải được ghi lại vào Nhật ký hệ thống (System Logs) phục vụ mục đích kiểm toán sau này.
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Nguyên tắc Đặc quyền Tối thiểu (Principle of Least Privilege - PoLP)
Phân hệ IAM của PronaFlow được xây dựng dựa trên nguyên tắc PoLP. Điều này đảm bảo rằng mỗi thực thể (người dùng hoặc dịch vụ) chỉ được cấp quyền truy cập vào những thông tin và tài nguyên thực sự cần thiết cho mục đích hợp pháp của họ. Việc này giảm thiểu tối đa bề mặt tấn công (Attack Surface) và rủi ro rò rỉ dữ liệu nội bộ.
## 4.2. Xác thực Đa yếu tố (Multi-Factor Authentication - MFA)
Cơ sở bảo mật của MFA dựa trên việc kết hợp các yếu tố xác thực khác nhau:
- **Knowledge:** Cái bạn biết (Mật khẩu).
- **Possession:** Cái bạn có (Điện thoại/Mã OTP). Việc yêu cầu cả hai yếu tố giúp tăng cường bảo mật theo cấp số nhân, vì kẻ tấn công khó có thể thỏa mãn cùng lúc cả hai điều kiện này.
## 4.3. Kiểm soát Truy cập Dựa trên Vai trò (RBAC - Role-Based Access Control)
Mô hình RBAC được lựa chọn thay vì phân quyền tùy ý (DAC) hoặc phân quyền bắt buộc (MAC) vì tính linh hoạt và khả năng quản trị phù hợp với mô hình doanh nghiệp. RBAC giúp chuẩn hóa các quy trình cấp quyền, giảm sai sót do con người khi quản lý quyền hạn của số lượng lớn người dùng.
