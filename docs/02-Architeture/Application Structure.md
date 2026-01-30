> The "Morden Data Science" Stack
> System Architecture Design: [[System Architecture Design.canvas|System Architecture Design]]

# A. Frontend: Client-Side

Hệ thống giao diện người dùng (Frontend) của Pronaflow được xây dựng dựa trên mô hình #SPA, áp dụng triệt để kiến trúc Component-Based Architecture.
Toàn bộ mã nguồn Frontend được đóng gói và tải xuống trình duyệt người dùng một lần duy nhất (hoặc tải lười - Lazy Loading). Việc giao tiếp với Backend chỉ diễn ra thông qua các RESTful API để trao đổi dữ liệu JSON, giúp tách biệt hoàn toàn tầng hiển thị (Presentation Layer) và tầng nghiệp vụ (Business Logic Layer).
Xem chi tiết: [[Frontend-Core| PronaFow - Frontend]]

```bash
frontend/src/
├── assets/                 # Tài nguyên tĩnh (Images, Global Styles, Fonts)
├── components/             # Các UI Components tái sử dụng (Button, Input, Modal)
│   ├── common/             # Components chung (LoadingSpinner, ErrorBoundary)
│   └── layout/             # Bố cục trang (Sidebar, Header, MainLayout)
├── config/                 # Cấu hình môi trường (API Base URL, Constants)
├── features/               # [QUAN TRỌNG] Phân chia theo module nghiệp vụ
│   ├── auth/               # Logic đăng nhập, đăng ký
│   ├── kanban/             # Logic bảng Kanban, Kéo thả
│   │   ├── components/     # Board, Column, TaskCard
│   │   ├── kanbanSlice.ts  # Redux State của Kanban
│   │   └── kanbanService.ts# API calls liên quan Kanban
│   ├── projects/           # Logic quản lý dự án
│   └── analytics/          # Logic biểu đồ, báo cáo
├── hooks/                  # Custom React Hooks (useAuth, useDebounce, useSocket)
├── pages/                  # Các trang màn hình chính (Route pages)
├── routes/                 # Cấu hình định tuyến (PublicRoutes, PrivateRoutes)
├── services/               # Cấu hình Axios Client, Interceptors (Xử lý Token)
├── types/                  # TypeScript Definitions (Interfaces, Types, Enums)
├── utils/                  # Các hàm tiện ích (FormatDate, Currency, Validators)
├── App.tsx                 # Component gốc
└── main.tsx                # Điểm khởi chạy ứng dụng
```

# B. Backend: Server
**Main Backend Service** đóng vai trò là "xương sống" của hệ thống PronaFlow. Phân hệ này chịu trách nhiệm xử lý toàn bộ logic nghiệp vụ cốt lõi, quản lý định danh, phân quyền và duy trì tính toàn vẹn của dữ liệu hệ thống.
- **Mô hình:** RESTful API.
- **Nguyên lý thiết kế:** Clean Architecture kết hợp với Domain-Driven Design ( #DDD).
- **Vai trò trong hệ thống phân tán:** Đóng vai trò là Orchestrator (Người điều phối), tiếp nhận yêu cầu từ Client (Web/Desktop) và điều phối các tác vụ sang các dịch vụ phụ trợ (như AI Service).
Xem chi tiết: [[Backend-Core-Service| Pronaflow Backend]]

```bash
backend-core/
├── app/
│   ├── api/
│   │   └── v1/              # Versioning API
│   │       ├── endpoints/   # Controllers (Projects, Tasks, Auth)
│   │       └── router.py    # URL Routing
│   ├── core/                # System Configuration
│   │   ├── config.py        # Environment Variables
│   │   └── security.py      # JWT Logic
│   ├── db/                  # Database Layer
│   │   ├── models/          # SQLAlchemy Models
│   │   └── repositories/    # CRUD Logic (Repository Pattern)
│   ├── schemas/             # Pydantic DTOs (Data Transfer Objects)
│   ├── services/            # Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   └── external/        # External Service Clients
│   │       └── ai_client.py # Giao tiếp với AI Server
│   └── main.py              # Application Entry Point
├── tests/                   # Unit & Integration Tests
└── requirements.txt
```
# C. Backend: AI Serving
**AI Serving Service** là một vi dịch vụ (Microservice) độc lập, chuyên biệt hóa cho các tác vụ Khoa học Dữ liệu. Nó được thiết kế để vận hành các mô hình học máy (Machine Learning Models) trong môi trường sản xuất, đảm bảo khả năng mở rộng (Scalability) và tối ưu hóa tài nguyên tính toán.
- **Mô hình:** Inference Server (Máy chủ suy luận).
- **Đặc tính:** Stateless (Không trạng thái) - Không lưu trữ dữ liệu nghiệp vụ lâu dài.
- **Input/Output:** Nhận dữ liệu thô (Raw Data) từ Main Backend -> Tiền xử lý -> Chạy Model -> Trả về kết quả dự báo (Prediction).

Xem chi tiết [[Backend-Inference-Service| PronaFlow AI Service]]

``` bash
ai-serving/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── prediction.py # API: /predict/duration, /predict/assignee
│   │   │   └── health.py     # Health Check (Dùng cho Docker/K8s)
│   │   └── router.py
│   ├── core/
│   │   ├── config.py         # Config đường dẫn Model, Hyperparameters
│   │   └── logging.py
│   ├── ml_engine/            # [CORE DATA SCIENCE]
│   │   ├── artifacts/        # Chứa file Binary Models (.pkl)
│   │   ├── pipelines/        # Logic tiền xử lý (Preprocessing transformers)
│   │   └── inference.py      # Singleton Class để Load Model & Predict
│   └── main.py
├── notebooks/                # Jupyter Notebooks (Dùng để thí nghiệm/Train model)
│   ├── 01_eda.ipynb
│   └── 02_training.ipynb
├── Dockerfile                # Môi trường chạy độc lập
└── requirements.txt          # Thư viện nặng (pandas, scikit-learn, torch)
```

# D. Desktop Wrapper: Application
Phân hệ Desktop của PronaFlow được xây dựng dựa trên mô hình **Hybrid Desktop Application** (Ứng dụng Lai). Chúng ta sử dụng **Electron.js** làm lớp bao đóng (Wrapper Layer), cho phép chạy ứng dụng Frontend (React) trong một môi trường Chromium được tùy biến riêng biệt, đồng thời có khả năng truy cập sâu vào API của hệ điều hành thông qua Node.js.
Kiến trúc này tuân thủ nguyên lý **"Write Once, Run Everywhere"**, đảm bảo sự nhất quán về trải nghiệm người dùng trên cả Windows, macOS và Linux mà không cần duy trì nhiều đội ngũ phát triển Native riêng biệt.
Xem chi tiết [[Desktop-Application-Wrapper| PronaFlow Desktop Wrapper]]

```bash
electron/
├── assets/                 # Icons (app.ico, app.icns)
├── build/                  # Cấu hình đóng gói (Installer config)
├── src/
│   ├── main/
│   │   ├── index.ts        # Entry point của Main Process
│   │   ├── window.ts       # Cấu hình cửa sổ browser
│   │   ├── ipc.ts          # Định nghĩa các luồng xử lý IPC
│   │   ├── menu.ts         # Native Application Menu
│   │   └── tray.ts         # System Tray configuration
│   ├── preload/
│   │   └── index.ts        # Preload script (Cầu nối bảo mật)
│   └── shared/             # Types chung chia sẻ với Frontend
├── package.json
└── electron-builder.yml    # Cấu hình build file .exe/.dmg
```