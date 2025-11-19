# Hướng dẫn Triển khai Lên Render (Cập nhật)

Dự án này được thiết kế để triển khai dễ dàng trên Render. Hãy làm theo các bước sau.

## Bước 1: Chuẩn bị các Secrets

Trước khi triển khai, bạn cần chuẩn bị sẵn các thông tin sau từ các dịch vụ cloud miễn phí:

1.  **Neo4j AuraDB:**
    *   `NEO4J_URI`
    *   `NEO4J_USER` (Thường là `neo4j`)
    *   `NEO4J_PASSWORD`
2.  **Qdrant Cloud:**
    *   `QDRANT_URL` (URL của cụm cluster)
    *   `QDRANT_API_KEY`
3.  **Hugging Face:**
    *   `HF_TOKEN` (Access Token với quyền `read`)
4.  **Gateway API Key:**
    *   `API_KEY` (Tạo một chuỗi bí mật của riêng bạn, ví dụ: dùng trình tạo mật khẩu)

## Bước 2: Fork và Triển khai trên Render

1.  **Fork Repository:** Fork repository này về tài khoản GitHub của bạn.
2.  **Tạo Blueprint trên Render:**
    *   Trên dashboard Render, vào mục **Blueprints** và bấm **New Blueprint Instance**.
    *   Kết nối tài khoản GitHub của bạn và chọn repository bạn vừa fork.
    *   Render sẽ tự động đọc file `render.yaml` và liệt kê tất cả các dịch vụ.
    *   Bấm **Apply** để Render bắt đầu tạo các dịch vụ. Quá trình build ban đầu có thể sẽ thất bại vì thiếu secrets, điều này là bình thường.

## Bước 3: Cấu hình Biến Môi trường (Secrets)

Đây là bước quan trọng nhất. Vì `render.yaml` chỉ định nghĩa *tên* của các secret, bạn cần phải cung cấp *giá trị* cho chúng.

1.  Sau khi Render đã tạo xong các dịch vụ từ Blueprint, hãy vào **Dashboard** của bạn.
2.  Bạn sẽ thấy một danh sách các dịch vụ (`gateway`, `graph-service`, `celery-worker`, v.v.).
3.  Với **từng dịch vụ** trong danh sách này, hãy làm như sau:
    *   Click vào tên dịch vụ.
    *   Chọn tab **Environment** ở menu bên trái.
    *   Bạn sẽ thấy một danh sách các biến môi trường. Những biến nào có giá trị rỗng (`value: ""`) trong `render.yaml` sẽ hiển thị ở đây để bạn điền vào.
    *   Click vào **"Add Environment Variable"** hoặc chỉnh sửa các biến hiện có, điền các giá trị bạn đã chuẩn bị ở **Bước 1**.
    *   **Ví dụ:** Cho dịch vụ `gateway`, bạn cần điền `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `QDRANT_URL`, `QDRANT_API_KEY`, `HF_TOKEN`, và `API_KEY`.
    *   Lặp lại quy trình này cho tất cả các dịch vụ (`graph-service`, `router-service`, `gnn-service`, `celery-worker`, `proactive-worker`).
4.  **Lưu và Triển khai lại:**
    *   Sau khi bạn đã thêm tất cả các secret cho một dịch vụ, hãy bấm **Save Changes**.
    *   Render sẽ tự động triển khai lại dịch vụ đó với các secret mới.
    *   Sau khi tất cả các dịch vụ đã được cập nhật và triển khai lại thành công, hệ thống của bạn sẽ hoạt động.

Giao diện Streamlit (`frontend`) sẽ có một URL công khai để bạn truy cập.
