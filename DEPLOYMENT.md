# Hướng dẫn Triển khai Lên Render

Dự án này được thiết kế để triển khai dễ dàng trên nền tảng Serverless của Render.

## Bước 1: Chuẩn bị

1.  **Tạo tài khoản:**
    *   Tạo tài khoản [GitHub](https://github.com/).
    *   Tạo tài khoản [Render](https://render.com/).
    *   Tạo tài khoản [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (Free tier).
    *   Tạo tài khoản [Qdrant Cloud](https://cloud.qdrant.io/) (Free tier).
    *   Tạo tài khoản [Hugging Face](https://huggingface.co/) và tạo một Access Token với quyền **write**.

2.  **Fork và Clone Repository:**
    *   Fork repository này về tài khoản GitHub của bạn.
    *   Clone nó về máy tính của bạn (tùy chọn).

## Bước 2: Cấu hình Secrets trên Render

1.  Trên dashboard của Render, vào mục **Blueprints**.
2.  Tạo một **Secret Group** mới và đặt tên là `twp-omega-secrets`.
3.  Thêm tất cả các biến môi trường từ file `.env.example` vào Secret Group này với các giá trị thực tế bạn đã lấy ở Bước 1.

## Bước 3: Triển khai

1.  Trên dashboard của Render, vào mục **Blueprints** và bấm **New Blueprint Instance**.
2.  Chọn repository GitHub bạn đã fork.
3.  Render sẽ tự động phát hiện file `render.yaml` và hiển thị kế hoạch triển khai.
4.  Bấm **Apply**.

Render sẽ bắt đầu xây dựng và triển khai tất cả các service. Sau vài phút, tất cả các endpoint sẽ hoạt động. Giao diện người dùng Streamlit của bạn cũng sẽ có một URL công khai.
