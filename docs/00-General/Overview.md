> Hồ sơ tổng quan dự án PronaFlow
> *Hệ thống Quản trị Dự án và Cộng tác Thông minh Đa nền tảng*

# 1. Đặt vấn đề và Lý do chọn đề tài
Trong bối cảnh chuyển đổi số diễn ra mạnh mẽ, nhu cầu quản lý công việc và tối ưu hóa quy trình làm việc nhóm là bài toán cấp thiết đối với mọi cá nhân và tổ chức. Các giải pháp hiện có trên thị trường thường rơi vào hai thái cực: quá đơn giản thiếu tính năng chuyên sâu, hoặc quá phức tạp với chi phí vận hành cao. Hơn thế nữa, đa số các công cụ này chưa tận dụng triệt để sức mạng của Khoa học Dữ liệu để hỗ trợ ra quyết định trong vòng đợi một dự án.
Xuất phát từ thực tế, dự án PronaFlow được xây dựng nhằm cung cấp một nền tảng quản trị dự án toàn diện, kết hợp giữa trải nghiệm người dùng hiện đại và khả năng phân tích dữ liệu thông minh, giúp các đội nhóm không chỉ "*quản lý*" mà còn "*tối ưu hóa*" hiệu suất làm việc.

# 2. Mục tiêu Dự án
## 2.1. Mục tiêu Tổng quát
Xây dựng hệ thống phân mềm hỗ trợ quản lý dự án theo mô hình "Agile/Kanban", cho phép triển khai linh hoạt trên cả nền tảng Web và Desktop (Windows/macOS), đảm bảo tính đồng bộ, bảo mật và hiệu năng cao.

## 2.2. Mục tiêu Cụ thể
1. Kiến trúc Đa nền tảng: Phát triển ứng dụng Web (Single Page Application - #SPA) và ứng dụng Desktop (Native executable) với cùng một sơ sở mã nguồn cốt lỗi.
2. Trãi nghiệm mượt mà: Tối ưu hóa tương tác người dùng (kéo thả, cập nhật thời gian thực) để giảm thiểu độ trễ trogn thao tác quản lý.
3. Tích hợp Trí tuệ nhân tạo (AI-Driven): Ứng dungj các thuật toán Học máy để phân tích dữ liệu dự án, từ đó đưa ra các gợi ý phân công nhân sự và dự báo tiến độ.
4. Khả năng mở rộng: Thiết kế hệ thống Backend theo hướng dịch vụ (Service-oriented) để dễ dàng tích hợp với các hệ sinh thái khác trong tương lai.
# 3. Kiến trúc Công nghệ (Technology Stack)
Dự án lựa chọn các công nghệ tiên tiến nhất hiện nay để đảm bảo tính thời thượng và hiệu năng, đặc biệt chú trọng vào khả năng tích hợp Data Science.

| Thành phần       | Công nghệ                   | Lý do lựa chọn và Dẫn chứng                                                                                                                                                                                                                                       |
| ---------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| #Frontend        | #React_js + #Vite           | Sử dụng kiến trúc Component-based giúp tải sử dụng mã nguồn hiệu quả. Cơ chế Virtual DOM của React đảm bảo hiệu năng cao cho các thao tác phức tạp như Kanban Board.                                                                                              |
| #Desktop-Wrapper | #Electron                   | Cho phép đóng gói ứng dụng Web thành phần mềm chạy trên hệ điều hành (`.exe`), tận dụng tài nguyên dự máy tính tốt hơn và hoạt động ngoại tuyến (offlien-first capability)                                                                                        |
| #Backend-API     | #Python-FastAPI             | Đây là trái tim của hệ thống. Python là ngôn ngữ chủ đạo của ngàng Khoa-học-Dữ-liệu, cho phép tích hợp trực tiếp các thư viện AI/ML vào luồng xử lý nghiệp vụ mà không cần qua trung gian. FastAPI cung câp hiệu năng xử lý bất đồng bộ (Asynchronous) vượt trội. |
| #Database        | #PostgreSQL                 | Hệ quản trị CSDL quan hệ mã nguồn mở mạnh mẽ nhất, hỗ trợ các kiểu dữ liệu phức tạp (JSONB) và mở rộng cho dữ liệu Vector (cần thiết cho AI RAG sau này).                                                                                                         |
| #AI-Engine       | #Scikit-learn / #TensorFlow | Module phân tích dữ liệu tích hợp sẵn trong Backend để thực heienj các tác vụ dự báo và gợi ý thông minh                                                                                                                                                          |
Xem chi tiết hơn về Kiến trúc phần mềm tại [[Application Structure]]
# 4. Đặc tả Các Phân hệ Chức năng
Hệ thống PronaFlow được kiến trúc dựa trên mô hình #Domain-Driven-Design ( #DDD), phân tách thành 10 phân hệ nghiệp vụ cốt lỗi. Mỗi phân hệ đóng vai trò một dịch vụ ( #Service) riêng biệt, đảm bảo tính gắn kết cao (High Cohesion) và phụ thuộc thấp (Low Coupling).

Xem chi tiết hơn về Các Phân hệ Chức năng tại [[System Functional Modules]]
# 5. Ý nghĩa Khoa học và Thực tiễn
Dự án PronaFlow không chỉ dừng lại ở việc tạo ra một phần mềm quản lý, mà còn là một nghiên cứu ứng dụng về việc đưa KHDL vào quy trình vận hành doanh nghiệp.
- Về mặt học thuật: Chứng minh khả năng xây dựng một hệ thống Full-stack hiện đại, bảo mật và có khả năng mở rộng. Áp dụng các thuật toán thống kê và học máy vào bài toán thực tế.
- Về mặt thực tiễn: Cung cấp một công cụ miễn phí, mã nguồn mở thay thế cho các phần mềm đắt đỏ, phù hợp với các đội nhóm khởi nghiệp hoặc môi trường học đường.

# 6. Kết luận 
PronaFlow là sự kết hợp hài hòa giữa Nghệ-thuật-Quản-trị và Khoa-học-Dữ-liệu. Với nền tảng công nghệ vững chắc và định hướng phát triển rõ ràng, dự án hứa hẹn mang lại trải nghiệm làm việc hiệu quả, minh bạch và thông minh cho người sử dụng.