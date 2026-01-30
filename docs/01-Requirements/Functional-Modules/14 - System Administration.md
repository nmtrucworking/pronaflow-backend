**Project**: PronaFlow
**Version**: 1.0
**State**: Draft
***Last updated:** Dec 31, 2025*

---
(Sẽ được viết sau khi hoàn thiện các tài liệu liên quan)
### 3. Phân loại Quản trị Hệ thống Chuyên biệt (Specialized Admin Roles)

Để đáp ứng tiêu chuẩn Enterprise, PronaFlow phân rã đội ngũ vận hành thành 18 vai trò admin chuyên trách nhằm kiểm soát rủi ro và tăng tính minh bạch.

- **Nhóm Vận hành Kỹ thuật:**
    
    - **Super Admin:** Quyền hạn cao nhất, chỉ sử dụng cho các tình huống khẩn cấp hoặc khôi phục hệ thống.
        
    - **System/SRE Admin:** Chịu trách nhiệm về hiệu năng và sức khỏe hệ thống, không truy cập dữ liệu người dùng.
        
    - **Release/Change Admin:** Kiểm soát quy trình phát hành và thay đổi mã nguồn.
        
- **Nhóm An ninh & Tuân thủ:**
    
    - **Security/Trust Admin:** Xử lý gian lận, lạm dụng và rủi ro bảo mật.
        
    - **IAM Admin:** Quản lý danh tính, phân quyền và cấu hình MFA.
        
    - **Compliance/Legal Admin:** Đảm bảo hệ thống tuân thủ các quy định pháp lý.
        
    - **Privacy/DPO:** Bảo vệ quyền riêng tư dữ liệu theo thiết kế (Privacy-by-design).
        
- **Nhóm Nghiệp vụ & Nội dung:**
    
    - **Finance Admin:** Quản lý doanh thu, gói dịch vụ và các giao dịch tài chính.
        
    - **AI/Automation Admin:** Quản lý hành vi của các mô hình AI và luồng tự động hóa.
        
    - **Data/Analytics Admin:** Đảm bảo chất lượng dữ liệu phục vụ phân tích mà không tiếp cận dữ liệu cá nhân thô.
        
    - **Support Admin:** Tiếp nhận và xử lý yêu cầu hỗ trợ (Ticket) từ người dùng.
        
- **Nhóm Kiểm toán:**
    
    - **Audit-only Admin:** Vai trò chỉ đọc, có quyền xem toàn bộ log hệ thống để phục vụ điều tra mà không thể thực hiện bất kỳ thao tác ghi nào.