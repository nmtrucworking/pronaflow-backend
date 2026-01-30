# 1. Core Technology Stack

| Thành phần            | Công nghệ         | Lý do lựa chọn                                                                                                                              |
| --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Serving Framework** | #FastAPI          | Nhẹ, độ trễ thấp (Low Latency), dễ dàng bọc (Wrap) các function Python thành API. (Có thể nâng cấp lên BentoML/TorchServe trong tương lai). |
| **ML Libraries**      | #Scikit-learn     | Thư viện tiêu chuẩn cho các thuật toán cổ điển (Regression, Clustering).                                                                    |
| **Data Processing**   | #Pandas / #NumPy  | Xử lý và biến đổi dữ liệu ma trận hiệu năng cao.                                                                                            |
| **Serialization**     | #Joblib / #Pickle | Định dạng lưu trữ và tải mô hình đã huấn luyện.                                                                                             |

# 2. Data Pipeline

Service này không kết nối trực tiếp vào Database chính (PostgreSQL) để đảm bảo nguyên tắc "Loose Coupling" (Liên kết lỏng). Dữ liệu cần thiết được truyền qua Payload của API Request.
## Luồng xử lý dự báo (Inference Flow)
1. **Receive:** Nhận JSON payload từ Main Backend (VD: Thông tin Task).
2. **Validation:** Kiểm tra định dạng dữ liệu đầu vào.
3. **Preprocessing:**
    - Làm sạch văn bản (NLP Cleaning).
    - Mã hóa biến phân loại (One-hot Encoding).
    - Chuẩn hóa dữ liệu số (Scaling).
4. **Inference:** Load Model (đã cache trong bộ nhớ) và thực hiện dự báo.
5. **Post-processing:** Định dạng kết quả đầu ra (VD: Chuyển xác suất 0.8 thành nhãn "High Priority").
6. **Response:** Trả về JSON kết quả.
# 3. Quản lý Mô hình (Model Management)
- **Artifact Store:** Các file model (`.pkl`, `.h5`, `.onnx`) được lưu trữ trong thư mục `artifacts/` và được quản lý phiên bản (Versioning) thông qua tên file hoặc Git LFS.
- **Hot Reloading:** (Nâng cao) Cơ chế cho phép cập nhật model mới mà không cần tắt server, bằng cách tải lại file artifact vào bộ nhớ khi có tín hiệu.
# 4. Các Mô hình Triển khai (Deployment Models)
## 4.1. Task Duration Predictor (Dự báo thời gian)
- **Loại:** Regression (Hồi quy).
- **Input:** Số lượng Subtask, Độ dài mô tả, Tags, Lịch sử người thực hiện.
- **Output:** Số giờ dự kiến (Float).
## 4.2. Assignee Recommender (Gợi ý nhân sự)
- **Loại:** Classification (Phân loại) hoặc Collaborative Filtering.
- **Input:** Tiêu đề Task, Yêu cầu kỹ năng (Tags).
- **Output:** Danh sách User ID phù hợp, sắp xếp theo độ khớp (Matching Score).