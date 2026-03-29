# PronaFlow Backend Documentation

Tài liệu được tổ chức lại theo 2 lớp:
- **Canonical docs**: tài liệu chuẩn để triển khai và vận hành hiện tại.
- **Legacy docs**: báo cáo/summary/checklist theo phase, dùng để tra cứu lịch sử.

## Start Here

1. [INDEX.md](INDEX.md) - điểm bắt đầu chính
2. [CANONICAL_MAP.md](CANONICAL_MAP.md) - bản đồ tài liệu chuẩn theo domain
3. [LEGACY_INDEX.md](LEGACY_INDEX.md) - chỉ mục tài liệu lịch sử
4. [STRUCTURE.md](STRUCTURE.md) - cấu trúc backend hiện hành

## Canonical Documentation

- [architecture/](architecture/) - kiến trúc hệ thống
- [api/](api/) - API reference theo version
- [database/](database/) - mô hình dữ liệu và migration
- [modules/](modules/) - tài liệu nghiệp vụ theo module
- [features/](features/) - cross-cutting capabilities
- [guides/](guides/) - hướng dẫn phát triển
- [deployment/](deployment/) - triển khai và vận hành

## Legacy Documentation

Các tài liệu phase/report/checklist vẫn được giữ nguyên ở root của [docs/](.) để đảm bảo tương thích link cũ.
Sử dụng [LEGACY_INDEX.md](LEGACY_INDEX.md) để tra cứu nhanh theo nhóm.

## Documentation Policy

- Tài liệu mới phải đặt vào các thư mục canonical theo domain.
- Không tạo thêm report mới ở root `docs/` nếu không bắt buộc.
- Nếu cập nhật tài liệu legacy, thêm ghi chú trạng thái và liên kết sang canonical doc tương ứng.

## Current Status

- Documentation organization: standardized navigation complete
- Backward compatibility: preserved (không di chuyển file lịch sử)
- Next step: chuẩn hóa dần nội dung trùng lặp giữa legacy và canonical

