**Dự án**: *PronaFlow - Hệ thống Quản trị Dự án và Cộng tác Thông minh Đa nền tảng*
**Kiến trúc**: `Microservices (Backend)` & `SPA/Desktop Hybrid (Frontend)`
**Trạng thái tài liệu**: Đảng cập nhật
***Last updated:** Dec 31, 2025*

---
# 1 - `/00-General` : Tổng quan & Nền tảng
Folder này chứa các thông tin định hướng chiến lược và nền tảng công nghệ cốt lỗi của dự án.
- Tổng quan dự án (Overview):
	- Xác định mục tiêu xây dựng hệ thống quản lý dự án theo mô hình "Agile/Kanban" kết hợp với Data Science.
	- Giải quyết bài toán "đảo thông tin" (Information Silos) và tích hợp AI để hỗ trợ ra quyết định.
	- Chi tiết tại: [[00-General/Overview|Overview.md]]
- Technology Stack (Kiến trúc công nghệ)
	- Frontend:
	- Backend - Core Service:
	- Backend - AI Inference:
	- Desktop Wrapper: Ứng dụng lai sử dụng `Electron.js`, hỗ trợ hoạt động ngoại tuyến (Offline-first).
	- Chi tiết tại: [[Technology-Stack | Technology-Stack.md]]
- Glossary (Thuật ngữ viết tắt của tài liệu kỹ thuật)
	- Trình bày các thuật ngữ, ký hiệu viết tắt trong toàn bộ Tài liệu Kỹ thuật hệ thống.
	- Chi tiết tại: [[Glossary.md]]
```bash
docs/
└── 00-General/
	├── Overview.md
	├── Technology-Stack.md
	└── Glossary.md
```

# 2 - `/01-Requirements` : Đặc tả Yêu cầu Hệ thống
Hệ thống được chia thành 16 phân hệ chức năng (Functional Modules) dựa trên tư duy thiết kế hướng tên miền ( #DDD)
- Danh sách các phân hệ chi tiết

- Xem chi tiết tại: [[System Functional Modules]]

```bash
docs/
└── 01-Requirements/
	├── Functional-Modules/
	│ ├── 01-Identity-Access-Management.md 
	│ ├── 02-MultiTenancy-Workspace.md 
	│ ├── 03-Project-Lifecycle-Management.md 
	│ ├── 04-Task-Execution-Orchestration.md 
	│ ├── 05-Temporal-Planning-Scheduling.md 
	│ ├── 06-Unified-Collaboration-Hub.md 
	│ ├── 07-Event-Driven-Notification.md 
	│ ├── 08-Data-Archiving-Compliance.md 
	│ ├── 09-User-Experience-Personalization.md 
	│ ├── 10-Intelligent-Decision-Support.md 
	│ ├── 11-Advanced-Analytics-Reporting.md
	│ ├── 12-Integration-Ecosystem.md
	│ ├── 13-Subscription-Billing.md
	│ ├── 14-System-Administration.md
	│ ├── 15-Help-Center-Knowledge-Base.md
	│ └── 16-User-Onboarding-Adoption.md
	└── Non-Functional.md
```

# 3 - `/02-Architecture` : Kiến trúc Hệ thống
Mô tả cấu trúc mã nguồn và sơ đồ hệ thống
- Application Structure:
	- Cấu trúc thư mục chi tiết cho:
		- Frontend
		- Backend
		- AI Enginee
		- Electron Wrapper
- System Architecture Design: 
	- Sơ đồ luồng dữ liệu giữa các thành phần Frontend, Backend, AI Service, Database
	- Chi tiết tại: [[System Architecture Design.canvas|System Architecture Design]]
- Architectural Decision Records (ADRs):
    - Ghi lại các quyết định kỹ thuật quan trọng (Why FastAPI? Why Electron?) để đảm bảo tính kế thừa tri thức.
    - Chi tiết tại thư mục: `/Decisions`
```bash
docs/
├── 02-Architecture/
	├── System-Architecture.canvas
	├── Application-Structure.md
	├── Database-Schema.md
	└── API-Design.md
	└── Decisions/
		├── ADR-001-TechStack-Selection.md
		└── ADR-Template.md
```

# 4 - `/03-UI-UX-Design`

```bash
docs/
└── 03-UI-UX-Design/                # Thiết kế giao diện
	├── Wireframes/                 # Hình ảnh hoặc link Figma
	└── Design-System.md            # Quy định về màu sắc, typography (dựa trên MUI)

```

# 5 - `/04-AI-Specifications`

- Data Goverance & Ethics:
	- Quy  định về nguồn gốc dữ liệu, quy trình ẩn danh hóa (Anonymization) và các biện pháp chống thiên kiến thuật toán (Bias Mitigation).
	- Chi tiết tại: [[Data-Goverance-Ethis|Data-Goverance-Ethis.md]]

```bash
docs/
└── 04-AI-Specifications/           # Đặc tả mô hình AI
	├── AI-Workflows.md
	├── Model-Card.md
	└── Data-Goverance-Ethis.md
```
# 6 - `/05-Deployment-Operations`
- Runbooks (Sổ tay vận hành):
	- Hướng dẫn xử lý các sự cố thường gặp (Troubleshooting) và quy trình khôi phục thảm họa (Disaster Recovery)
	- Chi tiết tại thư mục: `/Runbooks`

```bash
docs/
└── 05-Deployment-Operations/       # Vận hành & Triển khai
	├── Setup-Guide.md
	├── Docker-Strategy.md          # Kiến trúc Containerization
	└── Git-Workflow.md
	└── Runbooks/ # Xử lý sự cố vận hành 
		├── Troubleshooting.md 
		└── Backup-Restore-Procedures.md
```

# 7 - `/06-Quality-Assurance` : Đảm bảo Chất lượng
Thiết lập chiến lluocwj kiểm thử toàn diện cho hệ thống Hybrid (Web/Desktop) và AI.

- Testing Strategy:
	- Quy định công cụ và phạm vi cho Unit Test, Integration Test và E2E Test (Đặc biệt cho Electron App).
	- Chi tiết tại [[Testing-Strategy|Testing-Strategy.md]]
- AI Evaluation Metrics:
	- Các chỉ số đánh giá độ chính xác và hiệu năng của model  (Accuracy, F1-Score, Latency).
    - Chi tiết tại: [[AI-Evaluation-Metrics.md]]
- Security Audits:
    - Danh sách kiểm tra bảo mật định kỳ (Penetration Testing Checklist).


```bash
docs/
└── 06-Quality-Assurance/ 
	├── Testing-Strategy.md # Chiến lược test (Unit, Integration, E2E) 
	├── Security-Audit-Checklist.md # Danh sách kiểm tra bảo mật định kỳ 
	├── AI-Evaluation-Metrics.md
	└── Performance-Benchmarks.md
	
```