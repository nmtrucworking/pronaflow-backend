> Đặc trưng đã được ẩn danh - dùng cho inference & tranining
# Module 10

|Layer|Mục tiêu|Entity|
|---|---|---|
|Feature Store|Đặc trưng ML|FeatureSnapshot|
|Model Registry|Quản lý mô hình|MLModel, ModelVersion|
|Inference|Gợi ý & dự đoán|InferenceRequest, InferenceResult|
|Explanation|XAI|Explanation|
|Feedback|Học liên tục|UserFeedback|
|Monitoring|Drift & Quality|ModelMetric|
|Alert|Cảnh báo rủi ro|RiskSignal|
## Constraint:
- Không lưu PII
- Không join trực tiếp sang user profile
