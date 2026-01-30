Project**: PronaFlow
**Version**: 1.0
**State**: Draft
***Last updated:** Dec 31, 2025*

---
# 1. Business Overview
Trong kỷ nguyên "Product-led Growth", khả năng tự phục vụ (Self-service) của người dùng là yếu tố then chốt để mở rộng quy mô mà không làm phình to bộ phận Customer Support. Khi người dùng gặp khó khăn, họ muốn có câu trả lời ngay lập tức (Instant Gratification) thay vì chờ đợi phản hồi qua Email hay Ticket.
Phân hệ **Help Center & Knowledge Base** của PronaFlow được thiết kế với triết lý **"Just-in-Time Learning"** (Học ngay khi cần). Hệ thống không chỉ cung cấp một thư viện tài liệu thụ động, mà còn chủ động phân phối thông tin phù hợp với ngữ cảnh (Context-aware) mà người dùng đang thao tác.
Mục tiêu cốt lõi:
1. **Deflection:** Giảm 30-50% lượng Support Ticket bằng cách giải quyết vấn đề ngay tại nguồn.
2. **Enablement:** Giúp người dùng khai thác tối đa các tính năng nâng cao (như AI Prediction, Advanced Reports) thông qua tài liệu hướng dẫn chi tiết.
# 2. User Stories & Acceptance Criteria
## 2.1. Feature: Contextual Help Widget (Widget Hỗ trợ Ngữ cảnh)
### User Story 15.1
Là một Người dùng mới, khi tôi đang ở màn hình "Cấu hình Billing", Tôi muốn hệ thống gợi ý ngay các bài viết liên quan đến thanh toán mà không cần phải mở tab mới để tìm kiếm.
### Acceptance Criteria (#AC)
#### AC 1 - Route-based Suggestion (Gợi ý dựa trên định tuyến)
- **Logic:** Hệ thống mapping `Current URL Route` với `Article Tags`.
 - Ví dụ: User đang ở `/settings/billing` -> Widget hiển thị: "Cách thêm thẻ tín dụng", "Chính sách hoàn tiền".
 - User đang ở `/projects/kanban` -> Widget hiển thị: "Cách kéo thả task", "Thiết lập WIP Limit".
#### AC 2 - Embedded Reader
- Khi click vào bài viết gợi ý, nội dung mở ra trong một Panel trượt (Slide-over) hoặc Modal ngay trên giao diện hiện tại. Người dùng vừa đọc vừa thao tác được.
## 2.2. Feature: Semantic Search with AI (Tìm kiếm Ngữ nghĩa)
### User Story 15.2
Là một Người dùng không rành kỹ thuật, Tôi muốn gõ câu hỏi bằng ngôn ngữ tự nhiên (ví dụ: "Làm sao để đổi màu dự án?"), và hệ thống vẫn trả về bài viết "Hướng dẫn tùy biến Project Theme" dù không khớp từ khóa chính xác.
### Acceptance Criteria (#AC)
#### AC 1 - Vector Embeddings
- **Mechanism:** Sử dụng **Vector Search** (tích hợp qua Module 10 hoặc Service bên thứ 3 như Algolia/Pinecone).
- Hệ thống so sánh vector của câu truy vấn (Query) với vector của nội dung bài viết để tìm độ tương đồng về ý nghĩa (Semantic Similarity), thay vì chỉ so khớp chuỗi ký tự (Lexical Search).
#### AC 2 - Snippet Highlighting
- Kết quả tìm kiếm phải trích dẫn (Highlight) đoạn văn bản trả lời trực tiếp cho câu hỏi, giúp người dùng không phải đọc toàn bộ bài viết dài.
## 2.3. Feature: Documentation CMS (Hệ thống Quản trị Nội dung)
### User Story 15.3
Là một **Content Admin** (xem Module 14), Tôi muốn soạn thảo, định dạng và xuất bản các bài hướng dẫn có chứa hình ảnh và video minh họa, Để xây dựng kho tri thức cho người dùng.
### Acceptance Criteria (#AC)
#### AC 1 - Rich Text Editor
- Tích hợp trình soạn thảo WYSIWYG (như TipTap hoặc CKEditor) hỗ trợ:
 - Block code (cho developer).
 - Embed Video (YouTube/Loom).
 - Callout Blocks (Note, Warning, Info).
#### AC 2 - Versioning & Localization
- **Versioning:** Mỗi bài viết có thể có nhiều phiên bản (v1.0, v2.0) tương ứng với phiên bản phần mềm.
- **Localization:** Một bài viết gốc (English) có thể có nhiều bản dịch (Vietnamese, Japanese). Hệ thống tự động hiển thị bản ngữ phù hợp với cài đặt của người dùng (Module 9).
## 2.4. Feature: Feedback Loop (Vòng lặp Phản hồi)
### User Story 15.4
Là một Product Manager, Tôi muốn biết bài viết nào hữu ích và bài viết nào cần cải thiện, Để tối ưu hóa chất lượng tài liệu.
### Acceptance Criteria (#AC)
#### AC 1 - Sentiment Interaction
- Cuối mỗi bài viết có câu hỏi: _"Bài viết này có hữu ích không?"_ (Yes/No).
- Nếu chọn "No", hiển thị textbox tùy chọn để người dùng góp ý (ví dụ: "Ảnh minh họa bị lỗi", "Hướng dẫn khó hiểu").
#### AC 2 - Effectiveness Reporting
- Dashboard thống kê:
 - **Top Viewed:** Bài viết được đọc nhiều nhất.
 - **Helpfulness Score:** Tỷ lệ Yes/(Yes+No).
 - **Failed Searches:** Các từ khóa người dùng tìm kiếm nhưng không trả về kết quả (để Content Team viết bổ sung).
# 3. Business Rules & Technical Constraints
## 3.1. Quy tắc Quyền truy cập (Access Visibility)
- **Public KB:** Các bài viết hướng dẫn sử dụng cơ bản, FAQ được lập chỉ mục (Index) bởi Google để hỗ trợ SEO.
- **Private/Internal KB:** Các tài liệu về quy trình nội bộ, chính sách bảo mật nâng cao chỉ hiển thị cho người dùng đã đăng nhập (Logged-in Users) hoặc thuộc nhóm Enterprise.
## 3.2. Quy tắc Đồng bộ hóa (Synchronization)
- Khi một tính năng mới được **Product Admin** bật thông qua Feature Flag (Module 14), các tài liệu liên quan đến tính năng đó (đang ở trạng thái Draft) phải được tự động Publish hoặc hiển thị thông báo nhắc nhở Content Admin xuất bản.
## 3.3. Hiệu năng Tìm kiếm
- Thời gian phản hồi cho API tìm kiếm (Search Latency) phải **< 200ms**.
- Indexing: Khi một bài viết được cập nhật, dữ liệu tìm kiếm phải được Index lại trong vòng tối đa 5 phút.
# 4. Theoretical Basis (Cơ sở Lý luận)
## 4.1. Mô hình SECI (Nonaka & Takeuchi)
Module này hỗ trợ quá trình chuyển đổi tri thức:
- **Externalization (Ngoại hóa):** Chuyển tri thức ngầm (Tacit knowledge) trong đầu đội ngũ phát triển thành tri thức hiện hữu (Explicit knowledge) dưới dạng bài viết CMS.
- **Combination (Kết hợp):** Tổ chức, phân loại bài viết thành hệ thống phân cấp (Categories/Tags) để người dùng dễ tiếp cận.
## 4.2. Lý thuyết Tải nhận thức (Cognitive Load Theory)
Áp dụng vào tính năng **Contextual Help**:
- Thay vì bắt người dùng phải nhớ (Internalize) toàn bộ hướng dẫn sử dụng, hệ thống cung cấp "Bộ nhớ ngoài" (External Memory) ngay tại điểm thao tác.
- Việc này giảm **Extraneous Load** (Tải ngoại lai - thời gian tìm kiếm tài liệu), giúp người dùng tập trung vào **Germane Load** (Tải thiết yếu - thực hiện công việc).
## 4.3. Information Retrieval (Truy hồi thông tin)
Sử dụng mô hình **Hybrid Search** (kết hợp Keyword Search + Semantic Search):
- Keyword Search (BM25) tốt cho việc tìm các mã lỗi cụ thể hoặc tên tính năng chính xác.
- Semantic Search (Dense Retrieval) tốt cho việc hiểu ý định và các câu hỏi mơ hồ. Việc kết hợp cả hai đảm bảo độ chính xác (Precision) và độ phủ (Recall) cao nhất.
