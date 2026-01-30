# Bảng Mã Lỗi Hệ thống (System Error Codes)
Bảng định nghĩa các mã lỗi nghiệp vụ (Business Error Codes) được trả về trong phần `body` của phản hồi API, đi kèm với HTTP Status Code tương ứng. Frontend sẽ dựa vào `code` để hiển thị thống báo phù hợp.

|**Code**|**HTTP Status**|**Message Key (Frontend Mapping)**|**Default Message (VN)**|**Default Message (EN)**|**Context / Trigger**|
|---|---|---|---|---|---|
|**AUTH_001**|401|`auth.invalid_credentials`|Email hoặc mật khẩu không chính xác.|Invalid email or password.|Login thất bại.|
|**AUTH_002**|401|`auth.token_expired`|Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.|Session expired. Please login again.|Access Token hết hạn.|
|**AUTH_003**|403|`auth.forbidden`|Bạn không có quyền thực hiện hành động này.|You do not have permission to perform this action.|Vi phạm RBAC Middleware.|
|**SYS_429**|429|`sys.rate_limit_exceeded`|Quá giới hạn yêu cầu. Vui lòng thử lại sau.|Too many requests. Please try again later.|Chống Brute-force hoặc Spam API,.|
|**WS_001**|400|`workspace.invalid_name`|Tên không gian làm việc không hợp lệ (Chứa ký tự cấm).|Invalid workspace name.|Tạo Workspace mới.|
|**PROJ_001**|400|`project.invalid_date_range`|Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.|End date must be after or equal to start date.|Tạo/Sửa dự án.|
|**PROJ_002**|404|`project.not_found`|Dự án không tồn tại hoặc đã bị xóa.|Project not found or deleted.|Truy cập dự án sai ID.|
|**TASK_001**|400|`task.circular_dependency`|Phát hiện phụ thuộc vòng tròn (A->B->A). Không thể lưu.|Circular dependency detected. Cannot save.|Tạo quan hệ Task.|
|**BILL_001**|402|`billing.quota_exceeded`|Bạn đã đạt giới hạn của gói cước hiện tại. Vui lòng nâng cấp.|You have reached the limit of your current plan. Please upgrade.|Tạo quá 3 dự án (Free Plan).|
|**VAL_000**|422|`validation.generic_error`|Dữ liệu đầu vào không hợp lệ.|Validation error.|Lỗi kiểm tra Pydantic chung.|
|**SYS_500**|500|`sys.internal_error`|Lỗi hệ thống nội bộ. Vui lòng liên hệ Admin.|Internal server error. Please contact Admin.|Uncaught Exceptions.|