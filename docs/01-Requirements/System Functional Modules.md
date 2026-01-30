**Project**: PronaFlow
**Version**: 1.0
**State**: Draft
***Last updated:** Jan 9, 2026*

---
Hệ thống PronaFlow được kiến trúc dựa trên mô hình _Domain-Driven Design (DDD)_, phân tách thành 16 phân hệ nghiệp vụ cốt lõi.

| N.O | Function Modules                                 | Details                                                                                 |
| --- | ------------------------------------------------ | --------------------------------------------------------------------------------------- |
| 1   | Phân hệ Quản trị Định dang & Kiểm soát Truy cập  | [[System Functional Modules#1. Identity & Access Management - IAM\|Module 1]]           |
| 2   | Phân hệ Quản trị Đa Tổ chức                      | [[System Functional Modules#2. Multi-tenancy Workspace Governance\|Module 2]]           |
| 3   | Phân hệ Quản lý Vòng đời Dự án                   | [[System Functional Modules#3. Project Lifecycle Management\|Module 3]]                 |
| 4   | Phân hệ Điều phối & Thực thi Tác vụ              | [[System Functional Modules#4. Task Execution & Orchestration\|Module 4]]               |
| 5   | Phân hệ Lập lịch & Quản trị Thời gian            | [[System Functional Modules#5. Temporal Planning & Scheduling\|Module 5]]               |
| 6   | Phân hệ Truyền thông & Cộng tác Hợp nhất         | [[System Functional Modules#6. Unified Collaboration Hub\|Module 6]]                    |
| 7   | Phân hệ Thông báo Hướng Sự kiện                  | [[System Functional Modules#7. Event-Driven Notification System\|Module 7]]             |
| 8   | Phân hệ Lưu trữ & Tuân thủ Dữ liệu               | [[System Functional Modules#8. Data Archiving & Compliance\|Module 8]]                  |
| 9   | Phân hệ Cá nhân hóa Trải nghiệm                  | [[System Functional Modules#9. User Experience Personalization\|Module 9]]              |
| 10  | Phân hệ Hệ thống Hỗ trợ Ra quyết định Thông minh | [[System Functional Modules#10. Intelligent Decision Support System - IDSS\|Module 10]] |
| 11  | Phân hệ Báo cáo & Phân tích Nâng cao             | [[System Functional Modules#11. Advanced Analytics & Reporting\|Module 11]]             |
| 12  | Phân hệ Hệ sinh thái tích hợp & Mở rộng          | [[System Functional Modules#12. Integration Ecosystem\|Module 12]]                      |
| 13  | Phân hệ Gói cước & Thanh toán                    | [[System Functional Modules#13. Subscription & Billing Management\|Module 13]]          |
| 14  | Phân hệ Quản trị Hệ thống & Vận hành             | [[System Functional Modules#14. System Administration\|Module 14]]                      |
| 15  | Phân hệ Trung tâm Trợ giúp & Cơ sở Tri thức      | [[System Functional Modules#15. Help Center & Knowledge Base\|Module 15]]               |
| 16  | Phân hệ Dẫn nhập & Đào tạo Người dùng            | [[System Functional Modules#16. User Onboarding & Adoption\|Module 16]]                 |

# 1. Identity & Access Management - IAM
Đóng vai trò là **Security Gateway*** vận hành theo mô hình #AAA (Authentiacation - Authorization - Accounting), đảm bảo an ninh cho kiến trúc Multi-tenancy.
- **Identity Lifecycle & Authentication:** Quản lý trọn vẹn quy trình từ Đăng ký, Xác thực Email, đến Đăng nhập an toàn. Tích hợp cơ chế chống **Brute-force** (khóa tạm thời), hỗ trợ **MFA (TOTP)**, và đăng nhập qua mạng xã hội (**OAuth2** - Google/GitHub).
- **RBAC Authorization:** Thực thi kiểm soát truy cập dựa trên vai trò phân cấp (**Owner, Admin, Member, Guest**) tại từng điểm chạm (Endpoint), đảm bảo nguyên tắc đặc quyền tối thiểu (PoLP).
- **Session Governance:** Quản lý phiên làm việc chi tiết với giới hạn thiết bị đồng thời (**Concurrent Session Limit**), hỗ trợ thu hồi quyền truy cập từ xa (**Remote Revocation**) và phát hiện hành vi di chuyển bất thường (**Impossible Travel Alert**).
- **Account Security:** Quy trình khôi phục mật khẩu an toàn (One-time link) và cơ chế tự động chấm dứt phiên khi thay đổi thông tin nhạy cảm.
Xem chi tiết tại: [[1 - Identity and Access Management]]
# 2. Multi-tenancy Workspace Governance
Giải quyết bài toán vận hành đa tổ chức trên cùng một hạ tầng (SaaS Architecture), đảm bảo mỗi Workspace hoạt động như một thực thể độc lập.
- **Logical Isolation & Context Switching:** Thực thi nghiêm ngặt quy tắc cô lập dữ liệu (**Data Partitioning**) tại tầng Application/Database, đảm bảo người dùng chỉ truy cập được tài nguyên thuộc Workspace hiện hành. Hỗ trợ chuyển đổi ngữ cảnh làm việc (Context Switching) tức thì và lưu giữ trạng thái phiên.
- **Tenant Lifecycle Management:** Quản lý vòng đời toàn diện của tổ chức: Từ lúc Khởi tạo (bao gồm Default Workspace), Hoạt động, đến Xóa mềm (**Soft Delete**) và cơ chế tự động dọn dẹp (**Auto-Purge**) sau 30 ngày. Cung cấp công cụ Back-office cho System Admin để khôi phục (Restore) khi cần thiết.
- **Member & Role Governance:** Hệ thống phân quyền nội bộ linh hoạt với 4 vai trò chuẩn (**Owner, Admin, Member, Viewer**). Tích hợp quy trình mời thành viên qua **Magic Link**, quản lý **Owner Succession** (kế thừa quyền lực) và bảo vệ nghiêm ngặt quyền truy cập module Billing.
- **Workspace Configuration:** Cho phép tùy biến ngữ cảnh làm việc cụ thể cho từng tổ chức như: Lịch làm việc (**Working Schedule**), Múi giờ (Timezone) và Nhận diện thương hiệu (Branding).
Xem chi tiết tại: [[2 - Multi-tenancy Workspace Governance]]
# 3. Project Lifecycle Management
Đóng vai trò trung tâm điều phối vòng đời dự án từ khởi tạo, thực thi đến đóng và lưu trữ.
- **Lifecycle Control:** Quản lý quy trình dự án thông qua Máy trạng thái 5 bước (**Not-Started, In-Progress, In-Review, Done, Cancelled/Hold**) tích hợp các cổng kiểm soát (**Transition Gates**) như "Definition of Done". Hỗ trợ chiến lược lưu trữ (**Archiving**) tự động và chuyển giao quyền sở hữu (**Ownership Transfer**) an toàn.
- **Progressive Governance:** Cho phép lựa chọn chế độ quản trị linh hoạt: **Simple Mode** (Agile/Fast-paced) hoặc **Strict Mode** (Enterprise/Contract-based). Chế độ Strict kích hoạt các cơ chế kiểm soát nghiêm ngặt: Quản lý phiên bản **Baseline**, Quy trình yêu cầu thay đổi (**PCR - Project Change Request**), và Khóa vùng kế hoạch (**Freeze Window**).
- **Strategic Planning & Simulation:** Cung cấp môi trường **What-if Simulation** (Hộp cát mô phỏng) để PM tạo các kịch bản thử nghiệm (Scenarios) và đánh giá tác động trước khi áp dụng (Promote) vào dự án thật. Tự động tính toán chỉ số sức khỏe (**Project Health**) dựa trên Tiến độ, Nguồn lực và Ngân sách.
- **Standardization & Security:** Tổ chức dự án theo cấu trúc phân cấp (**Portfolios/Programs**). Chuẩn hóa khởi tạo qua **Project Templates** và hệ thống phân quyền chuyên sâu cấp dự án (**PM, Planner, Member, Viewer**) hỗ trợ chế độ riêng tư (Private Projects).
Xem chi tiết tại: [[3 - Project Lifecycle Management]]
# 4. Task Execution & Orchestration
Được thiết kế để tối ưu hóa hiệu suất thực thi và đảm bảo kỷ luật vận hành xoay quanh đơn vị công việc (Task).
- **WBS & Atomic Units:** Quản lý cấu trúc phân rã công việc đa tầng (**Task List -> Task -> Subtask**) và các thuộc tính mở rộng (**Custom Fields**), hỗ trợ định nghĩa các cột mốc (**Milestones**) quan trọng.
- **Productivity Tools:** Cung cấp bộ công cụ tăng tốc độ làm việc: **Time Tracking** (Theo dõi thời gian thực), **Task Templates** (Mẫu công việc chuẩn hóa), **Recurring Tasks** (Công việc lặp lại tự động) và Thao tác hàng loạt (**Bulk Actions**).
- **Orchestration & Logic:** Quản lý chặt chẽ sự phụ thuộc (**Dependencies - FS**) với cơ chế phát hiện vòng lặp (**Cycle Detection**).
- **Execution Discipline:** Thực thi các ràng buộc từ kế hoạch tổng thể (**Locked Plan**). Hệ thống phân biệt rõ ràng giữa "Ngày kế hoạch" (cố định bởi Module 5) và "Ngày thực tế" (linh hoạt ghi nhận) để đo lường độ trễ chính xác mà không làm gián đoạn dòng chảy công việc.
Xem chi tiết tại: [[4 - Task Execution and Orchestration]]
# 5. Temporal Planning & Scheduling
Phân hệ hoạch định chiến lược và quản trị thời gian chuyên sâu, đóng vai trò là "bộ não" tính toán lịch trình cho các dự án quy mô lớn (Waterfall/Hybrid).
- **Advanced Gantt & CPM:** Trực quan hóa tiến độ trên biểu đồ Gantt tương tác (Drag & Drop), hỗ trợ đầy đủ các loại phụ thuộc chuẩn PDM (**FS, SS, FF, SF**) cùng tham số **Lag/Lead Time**. Tự động tính toán Đường găng (**Critical Path**) và lan truyền thay đổi lịch trình (**Auto-Scheduling**) theo thời gian thực.
- **Planning Governance & Simulation:** Thiết lập kỷ luật kế hoạch thông qua quy trình phê duyệt và quản lý phiên bản **Baseline**. Cung cấp môi trường **What-If Simulation** (Hộp cát mô phỏng) để PM thử nghiệm các kịch bản thay đổi và xem trước bảng phân tích tác động (**Change Impact Analysis**) trước khi áp dụng vào dữ liệu thật. Hỗ trợ **Freeze Window** để khóa cứng lịch trình ngắn hạn.
- **Resource Optimization:** Tự động phát hiện xung đột và cân bằng nguồn lực (**Automated Resource Leveling**) dựa trên độ trôi (Float) và độ ưu tiên. Tích hợp xử lý ngoại lệ lịch biểu cá nhân (Calendar Exceptions) và chia tách công việc (**Task Splitting**).
- **SLA & Risk Management:** Theo dõi cam kết dịch vụ (**SLA Tracking**) chính xác theo giờ hành chính (Business Hours). Hỗ trợ lập lịch dựa trên rủi ro (**Risk-aware Scheduling**) với dự báo ngày hoàn thành theo xác suất (P50/P90) và quản lý phụ thuộc đa dự án (**Cross-Project Dependencies**).
Xem chi tiết tại: [[5 - Temporal Planning and Scheduling]]
# 6. Unified Collaboration Hub
Chuyển đổi từ giao tiếp phân mảnh sang mô hình **Contextual Communication** (Giao tiếp gắn liền ngữ cảnh), đóng vai trò là "Nguồn sự thật duy nhất" (Single Source of Truth) cho mọi trao đổi dự án.
- **Contextual Discussion:** Hỗ trợ thảo luận đa cấp (**Threaded Replies**) ngay trong Task, tích hợp soạn thảo văn bản (Rich Text) và định danh thông minh (**Smart Mentions**).
- **Digital Asset Management (DAM):** Quản lý tài sản số tập trung với khả năng kiểm soát phiên bản (**Versioning**), xem trước đa định dạng (**Universal Viewer**) và quy trình phê duyệt chính thức (**Formal Approval Workflow**) có kiểm toán chữ ký số.
- **Real-time Collaboration:** Tích hợp chỉ báo hiện diện (**Presence Indicators**) để biết ai đang xem/soạn thảo, ngăn chặn xung đột dữ liệu.
- **Integrated Knowledge Base (Wiki):** Hệ thống ghi chú dự án và cá nhân (Notes) hỗ trợ cấu trúc phân cấp, mẫu (**Templates**), liên kết thông minh (**Smart Backlinks**) và lịch sử thay đổi tài liệu (**Diff View**). Cho phép xuất bản tài liệu ra công chúng (**Public Publishing**) với kiểm soát truy cập.
Xem chi tiết tại: [[6 - Unified Collaboration Hub]]
# 7.  Event-Driven Notification System
- Pub/Sub Machanism: Sử dụng kiến trúc Publish/Subscribe để xử lý hàng triệu sự kiện hệ thống theo thời gian thực.
- Smart Routing: Phân loại và định tuyến thông báo thông minh đến đúng đối tượng, qua đúng kênh (In-app, Email, Push) để giảm thiểu nhiễu thông tin.
Xem chi tiết tại: [[7 - Even-Driven Notification System]]
# 8. Data Archiving & Compliance
- Data Retention Policy: Thiết lập các quy tắc tự động về lưu trữ và xóa dữ liệu (Soft Delete/ Hard Delete) tuân thủ các quy định bảo mật.
- Cold Storage Strategy: Cơ chế di chuyển dữ liệu ít truy cập (dự án đã đóng) sang vùng lưu trữ lạnh để tối ưu hiệu năng truy cập cho hệ thống chính (Hot Data).
Xem chi tiết tại: [[8 - Data Archiving and Compliance]]
# 9. User Experience Personalization
- L18n & L10n: Hỗ trợ Quốc tế hóa (Internationalization) và Bản địa hóa (Localization) toàn diện cho giao diện và dữ liệu/
- Adaptive UI: Cho phép người dùng tuy biến Theme, Layout và Dashboard cá nhân hóa để phù hợp với thói quan làm việc (Ergonomics).
Xem chi tiết tại: [[9 - User Experience Personalization]]
# 10. Intelligent Decision Support System - IDSS
Đây là phân hệ nâng cao, tận dụng nền tảng Data Science để chuyển đổi dữ liệu thô thành tri thức quản trị.
- Predictive Analytics: Sử dụng các mô hình hồi quy (Regression Models) để dự báo ngày hoàn thành dự án dựa trên vận tốc làm việc lịch sử.
- Prescriptive Analytics: Ứng dụng thuật toán gợi ý để đề xuất phân công nhân sự tối ưu dựa trên kỹ năng (Skill-set) và tải công việc.
- Anomaly Detection: Tự động phát hiện các hành vi bất thường trong hệ thống hoặc các dự án có nguy cơ rủi ro cao.
Xem chi tiết tại: [[10 - Intelligent Decision Support System]]
# 11. Advanced Analytics & Reporting
Cung cấp góc nhìn sâu sắc về hiệu suất vận hành doanh nghiệp thông qua dữ liệu lịch sử.
- **Descriptive Analytics**: Báo cáo tổng hợp đa chiều về tiến độ, phân bổ nguồn lực và chi phí (Burn-down, Velocity, Resource Heatmap).
- **Time Tracking & Timesheets**: Ghi nhận thời gian thực tế (Billable/Non-billable Hours) phục vụ công tác kế toán và tính lương.
- **Custom Report Builder**: Cho phép người dùng tự định nghĩa báo cáo (Ad-hoc Reporting) bằng thao tác kéo thả. 
Xem chi tiết tại: [[11 - Advanced Analytics and Reporting]]
# 12. Integration Ecosystem
Mở rộng khả năng của PronaFlow thông qua việc kết nối với các hệ thống bên ngoài.
- **API Gateway & Webhooks**: Cung cấp cơ chế giao tiếp chuẩn (RESTful/GraphQL) để các bên thứ 3 (GitLab, Figma, Slack) tích hợp quy trình.
- **Marketplace**: Kho ứng dụng tập trung (Plugin Architecture) cho phép cài đặt và quản lý các tiện ích mở rộng.
- **Connector Hub**: Các đầu nối (Connectors) dựng sẵn giúp đồng bộ dữ liệu hai chiều (Bi-directional Sync) mà không cần viết code (No-code Integration). Xem chi tiết tại: [[12 - Integration Ecosystem]]
# 13. Subscription & Billing Management
Hệ thống quản trị tài chính và cấp phép sử dụng tài nguyên (Resource Provisioning).
- **Plan Management**: Định nghĩa các gói dịch vụ (Tiered Pricing) và hạn ngạch tài nguyên (Quotas) cho từng gói (User limit, Storage limit).
- **Automated Billing Cycle**: Tự động hóa quy trình tính cước (Recurring Billing), xuất hóa đơn (Invoicing) và xử lý gia hạn.
- **Usage Metering**: Đo đếm mức độ sử dụng tài nguyên thực tế (API calls, AI tokens) để phục vụ mô hình tính phí theo nhu cầu (Pay-as-you-go). 
Xem chi tiết tại: [[13 - Subscription and Billing Management]]
# 14. System Administration
Phân hệ dành riêng cho Super Admin để giám sát và vận hành toàn bộ hệ thống (Back-office).
- **Global Tenant Management**: Quản lý vòng đời của tất cả các Tenant (Onboard, Suspend, Offboard).
- **Operational Observability**: Dashboard giám sát sức khỏe hệ thống (Health Check), xem log lỗi tập trung và theo dõi hiệu năng (APM).
- **Feature Flags**: Quản lý bật/tắt tính năng mới theo từng nhóm người dùng (A/B Testing) mà không cần redeploy. 
Xem chi tiết tại: [[14 - System Administration]]
# 15. Help Center & Knowledge Base
Hệ thống tự phục vụ (Self-service) giúp giảm tải cho bộ phận hỗ trợ kỹ thuật.
- **Contextual Help**: Nhúng tài liệu hướng dẫn (Embedded Docs) ngay tại nơi người dùng gặp khó khăn (Context-aware Widgets).
- **CMS for Documentation**: Hệ thống quản lý nội dung bài viết, FAQ, Release Notes với khả năng tìm kiếm ngữ nghĩa (Semantic Search).
- **Feedback Loop**: Thu thập đánh giá của người dùng về độ hữu ích của bài viết để liên tục cải thiện chất lượng tài liệu. 
Xem chi tiết tại: [[15 - Help Center and Knowledge Base]]
# 16. User Onboarding & Adoption
Tối ưu hóa trải nghiệm người dùng mới và thúc đẩy hành vi sử dụng sản phẩm.
- **Interactive Walkthroughs**: Các tour hướng dẫn từng bước (Step-by-step Guides) phủ lên giao diện ứng dụng để đào tạo người dùng (In-app Training).
- **Progress Tracking**: Theo dõi tiến độ hoàn thành các bước thiết lập hồ sơ (Onboarding Checklist).
- **Feature Discovery**: Giới thiệu tính năng mới thông qua các thông báo định hướng (Tooltips/Hotspots) dựa trên hành vi người dùng. 
Xem chi tiết tại: [[16 - User Onboarding and Adoption]]