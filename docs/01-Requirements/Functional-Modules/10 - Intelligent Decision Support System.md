Project**: PronaFlow
**Version**: 1.0
**State**: Draft
_Last updated: Dec 31, 2025_

---

> ⚠️ **THÔNG BÁO QUAN TRỌNG**
> 
> **Module 10 - Intelligent Decision Support System sẽ được triển khai trong PronaFlow Version 2.0**
> 
> Phiên bản hiện tại (v1.x) tập trung vào các module cốt lõi của hệ thống quản trị dự án. Các tính năng AI/ML Decision Support sẽ được phát triển trong lộ trình phát triển tiếp theo.

---

# 1. Business Overview

Trong các hệ thống quản trị dự án truyền thống, việc ra quyết định (ví dụ: gán việc cho ai, ước lượng thời gian bao lâu) thường dựa hoàn toàn vào trực giác (Intuition-based) hoặc kinh nghiệm chủ quan của người quản lý. Điều này dễ dẫn đến các sai số như "Lạc quan quá mức" (Optimism Bias) hoặc phân bổ nguồn lực không đồng đều.

Phân hệ **Intelligent Decision Support System (IDSS)** của PronaFlow chuyển đổi mô hình quản trị sang **Data-Driven** (Dựa trên dữ liệu). Bằng cách khai thác kho dữ liệu lịch sử khổng lồ của dự án thông qua các thuật toán Học máy (Machine Learning), phân hệ này đóng vai trò như một "Cố vấn ảo", cung cấp các tham số khách quan để tối ưu hóa quy trình ra quyết định.

# 2. User Stories & Acceptance Criteria

## 2.1. Feature: Predictive Task Estimation (Dự báo Thời lượng Công việc)

### User Story 10.1

Là một Quản lý dự án, khi tôi tạo một Task mới, Tôi muốn hệ thống gợi ý thời gian thực hiện (Estimated Hours) dựa trên độ phức tạp và lịch sử các task tương tự, Để giảm thiểu việc ước lượng sai lệch (Underestimation).

### Acceptance Criteria (#AC)

#### AC 1 - Inference Trigger

- **Event:** Ngay khi người dùng nhập xong `Title`, `Description` và chọn `Tags`.
    
- **Action:** Hệ thống gửi request bất đồng bộ (Async Request) sang _Inference Service_.
    
- **Display:** Hiển thị một con số gợi ý (ví dụ: "Gợi ý: 4.5h") bên cạnh trường nhập liệu thời gian.
    

#### AC 2 - Confidence Interval (Khoảng tin cậy)

- Hệ thống không chỉ trả về một con số đơn lẻ (Point Estimate) mà cung cấp một khoảng tin cậy 95% (ví dụ: "3h - 6h") để người quản lý biết mức độ chắc chắn của mô hình.
    

## 2.2. Feature: Smart Assignee Recommendation (Gợi ý Phân công Nhân sự)

### User Story 10.2

Là một Quản lý dự án, Tôi muốn hệ thống đề xuất danh sách nhân sự phù hợp nhất cho một đầu việc cụ thể, dựa trên kỹ năng và tải công việc hiện tại của họ, Để đảm bảo "đúng người đúng việc".

### Acceptance Criteria (#AC)

#### AC 1 - Ranking Logic (Logic Xếp hạng)

- Hệ thống trả về danh sách Top 3 ứng viên, được sắp xếp dựa trên điểm số phù hợp (Matching Score).
    
- **Matching Score** được tính toán tổng hợp từ:
    
    1. **Skill Match:** Mức độ khớp giữa `Task Tags` (yêu cầu) và `User Skills`.
        
    2. **History Match:** User đã từng làm các Task tương tự trong quá khứ chưa?
        
    3. **Availability:** User có đang bị quá tải (Overloaded) trong khoảng thời gian dự kiến không?
        

#### AC 2 - Explanation (Khả năng giải thích)

- Đi kèm với mỗi gợi ý phải có lý do ngắn gọn (Explainable AI).
    
    - _Ví dụ:_ "Nguyễn Văn A (Score: 92% - Đã làm 5 task tương tự, Đang rảnh)".
        

## 2.3. Feature: Project Risk Anomaly Detection (Phát hiện Bất thường Rủi ro)

### User Story 10.3

Là một Stakeholder, Tôi muốn nhận được cảnh báo sớm nếu một dự án đang có dấu hiệu đi chệch hướng, ngay cả khi trạng thái trên báo cáo vẫn là "Màu xanh", Để kịp thời can thiệp.

### Acceptance Criteria (#AC)

#### AC 1 - Velocity Analysis (Phân tích Vận tốc)

- Hệ thống theo dõi tốc độ hoàn thành công việc (Burn-down rate) thực tế so với kế hoạch.
    
- Nếu phát hiện sự suy giảm đột ngột (Sudden Drop) hoặc sự đình trệ kéo dài (Stagnation) vượt quá ngưỡng cho phép (Threshold), hệ thống kích hoạt cờ cảnh báo rủi ro.
    

# 3. Business Rules & Technical Constraints

## 3.1. Quy tắc Bảo mật Dữ liệu (Privacy-Preserving Rules)

- **Anonymization:** Khi huấn luyện lại mô hình (Re-training), dữ liệu định danh cá nhân (PII) như Tên, Email phải được mã hóa hoặc loại bỏ. Chỉ giữ lại các đặc trưng hành vi (Behavioral Features).
    
- **Scope Isolation:** Mô hình gợi ý cho Workspace A chỉ được học từ dữ liệu của Workspace A (hoặc dữ liệu ẩn danh toàn cục), tuyệt đối không để lộ dữ liệu nhạy cảm (Data Leakage) giữa các đối thủ cạnh tranh dùng chung hệ thống.
    

## 3.2. Quy tắc Ngưỡng tin cậy (Confidence Threshold)

- Để tránh gây nhiễu, hệ thống chỉ hiển thị gợi ý khi Mô hình AI đạt độ tin cậy > **70%**.
    
- Nếu độ tin cậy thấp hơn, UI sẽ ẩn phần gợi ý và để người dùng tự quyết định (Fallback to Manual).
    

# 4. Theoretical Basis (Cơ sở Lý luận)

## 4.1. Hồi quy Tuyến tính & Phi tuyến (Regression Analysis)

Áp dụng cho bài toán **Dự báo Thời lượng (Feature 10.1)**.

- **Mô hình:** Sử dụng thuật toán _Gradient Boosting Regressor_ (như XGBoost hoặc LightGBM) vì khả năng xử lý tốt cả dữ liệu số (số lượng subtask) và dữ liệu phân loại (Tags, Priority).
    
- **Input Features:** Độ dài mô tả (Word count), Số lượng Subtask, Tags, Độ ưu tiên.
    
- **Target Variable:** Thời gian thực tế hoàn thành (Actual Duration).
    

## 4.2. Hệ gợi ý dựa trên Nội dung (Content-based Filtering)

Áp dụng cho bài toán **Gợi ý Nhân sự (Feature 10.2)**.

- **Nguyên lý:** Xây dựng Vector đặc trưng (Feature Vector) cho Task và cho User trong cùng một không gian n chiều.
    
- **Thuật toán:** Sử dụng độ tương đồng Cosine (Cosine Similarity) để đo khoảng cách giữa Vector Task và Vector User.
    
    $$Similarity(A, B) = \frac{A \cdot B}{||A|| \times ||B||}$$
- Người có Vector kỹ năng gần nhất với Vector yêu cầu của Task sẽ được gợi ý cao nhất.
    

## 4.3. Kiểm soát Quá trình Thống kê (Statistical Process Control - SPC)

Áp dụng cho bài toán **Phát hiện Bất thường (Feature 10.3)**.

- Sử dụng biểu đồ kiểm soát (Control Charts) để theo dõi tiến độ dự án.
    
- Mọi điểm dữ liệu (Tiến độ ngày) nằm ngoài giới hạn kiểm soát trên/dưới (Upper/Lower Control Limits - $3\sigma$) đều được coi là "Bất thường" (Anomaly) cần cảnh báo, thay vì chỉ dựa vào cảm tính.