# 🏁 Hướng dẫn Triển khai Dự án trên Máy mới

Bộ tài liệu này giúp bạn tái hiện lại 100% môi trường Oracle AI (290,000 bản ghi đánh giá sản phẩm) trên một máy tính hoàn toàn mới.

## 🛠️ Bước 1: Chuẩn bị Môi trường (Prerequisites)

Bạn cần cài đặt các thành phần sau trên máy mới:
1. **Docker & Docker Compose**: Để chạy container Oracle 26ai.
2. **Python 3.10+**: Để chạy các script đồng bộ.
3. **NVIDIA Driver** (Tùy chọn): Nếu bạn muốn tiếp tục vector hóa thêm dữ liệu bằng GPU Blackwell.

## 🔑 Bước 2: Lấy mã nguồn & Cấu hình

Mở terminal trên máy mới và chạy các lệnh sau:

```bash
# 1. Clone mã nguồn từ GitHub
git clone https://github.com/congkx123789/He_quan_tri.git
cd He_quan_tri

# 2. Tạo file cấu hình bảo mật
cp .env.example .env
# Mở file .env và dán mã HF_TOKEN của bạn vào (Token có quyền Write/Read)
```

## 🚀 Bước 3: Triển khai Một-chạm (One-Touch Restore)

Đây là bước quan trọng nhất. Chỉ cần chạy script sau, hệ thống sẽ tự động làm mọi việc cho bạn:

```bash
chmod +x scripts/auto_restore.sh
./scripts/auto_restore.sh
```

### Script này sẽ làm gì?
- Tạo môi trường ảo Python và cài đặt thư viện Hugging Face.
- Tải bản Snapshot **1.6GB** từ kho Hugging Face của bạn.
- Khởi động container Oracle AI Database.
- Thực hiện lệnh **Data Pump Import** để đưa 290.000 bản ghi và bộ chỉ mục Vector vào database.

## 🔍 Bước 4: Kiểm tra hoạt động

Sau khi script chạy xong, bạn có thể kiểm tra dữ liệu qua script test hặc SQL:

```bash
# Chạy script test tìm kiếm AI
python3 python/test_semantic_search.py
```

## 🛠️ Xử lý sự cố thường gặp
- **Lỗi 401 trên Hugging Face**: Kiểm tra lại `HF_TOKEN` trong file `.env`.
- **Lỗi Docker Permissions**: Đảm bảo user của bạn đã được thêm vào group docker (`sudo usermod -aG docker $USER`).

---
*Crafted by Antigravity for Local Enterprise AI Final Handover.*
