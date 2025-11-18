# Hướng dẫn Triển khai Lên Render (Cập nhật)

Dự án này được thiết kế để triển khai dễ dàng trên nền tảng Serverless của Render. Quy trình đã được đơn giản hóa để bạn không cần phải tạo Secret Group thủ công.

## Bước 1: Chuẩn bị Nền tảng

1.  **Tạo các tài khoản cần thiết:**
    *   Tạo tài khoản [GitHub](https://github.com/).
    *   Tạo tài khoản [Render](https://render.com/).
    *   Tạo tài khoản [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (Free tier) và ghi lại **URI, User, Password**.
    *   Tạo tài khoản [Qdrant Cloud](https://cloud.qdrant.io/) (Free tier) và ghi lại **URL cụm cluster và API Key**.
    *   Tạo tài khoản [Hugging Face](https://huggingface.co/) và tạo một [Access Token](https://huggingface.co/settings/tokens) với quyền **read**.
    *   Tạo một API Key của riêng bạn (ví dụ: dùng trình tạo mật khẩu) để bảo vệ Gateway.

2.  **Fork Repository:**
    *   **Fork** repository này về tài khoản GitHub của bạn.

## Bước 2: Triển khai trên Render

1.  Trên dashboard của Render, vào mục **Blueprints** và bấm **New Blueprint Instance**.
2.  Kết nối tài khoản GitHub của bạn và chọn repository bạn vừa fork.
3.  **Quan trọng:** Render sẽ tự động phát hiện file `render.yaml` và chuyển bạn đến trang cấu hình. Tại đây, nó sẽ **tự động hiển thị các ô để bạn nhập các giá trị bí mật** (`NEO4J_URI`, `QDRANT_API_KEY`, `API_KEY`, v.v.).
4.  Cẩn thận điền tất cả các giá trị bạn đã chuẩn bị ở Bước 1 vào các ô tương ứng.
5.  Sau khi điền xong, bấm **Apply**.

Render sẽ bắt đầu xây dựng và triển khai tất cả các dịch vụ. Quá trình này có thể mất vài phút. Sau khi hoàn tất, giao diện Streamlit của bạn sẽ có một URL công khai và hệ thống sẽ sẵn sàng để sử dụng.
