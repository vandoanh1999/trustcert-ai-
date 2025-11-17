# Hướng dẫn Cấu hình Secrets cho Google Sheets

Để hệ thống có thể ghi lại phản hồi vào Google Sheet của bạn, bạn cần tạo một "Service Account" và chia sẻ Sheet đó với tài khoản này.

## Bước 1: Tạo Google Service Account và Credentials

1.  **Truy cập Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Tạo một dự án mới** (hoặc chọn một dự án có sẵn).
3.  **Bật APIs:**
    *   Vào "APIs & Services" > "Library".
    *   Tìm và bật "Google Drive API".
    *   Tìm và bật "Google Sheets API".
4.  **Tạo Service Account:**
    *   Vào "IAM & Admin" > "Service Accounts".
    *   Bấm "Create Service Account". Đặt tên cho nó (ví dụ: `twp-omega-feedback-writer`).
    *   Bỏ qua các bước cấp quyền truy cập vào dự án (không cần thiết).
5.  **Tạo Key:**
    *   Tìm Service Account bạn vừa tạo trong danh sách, bấm vào nó.
    *   Đi đến tab "Keys".
    *   Bấm "Add Key" > "Create new key".
    *   Chọn **JSON** và bấm "Create". Một file `.json` sẽ được tải về máy của bạn.

## Bước 2: Tạo và Chia sẻ Google Sheet

1.  **Tạo một Google Sheet mới:** [https://sheets.new](https://sheets.new)
2.  Đặt tên cho nó, ví dụ: "TWP-Omega Feedback".
3.  Trong sheet đầu tiên (Sheet1), đổi tên thành `Feedback`.
4.  Tạo 4 cột đầu tiên với các tiêu đề sau: `Timestamp`, `Question`, `Incorrect Answer`, `Correct Answer`.
5.  **Lấy địa chỉ email của Service Account:** Mở file `.json` bạn đã tải về, tìm trường `client_email`. Nó sẽ trông giống như: `...gserviceaccount.com`.
6.  **Chia sẻ Sheet:**
    *   Bấm nút "Share" ở góc trên bên phải của Google Sheet.
    *   Dán địa chỉ email của Service Account vào ô chia sẻ.
    *   Cấp quyền **Editor** cho nó.
    *   Bấm "Send".

## Bước 3: Thêm Credentials vào Streamlit Secrets

1.  Mở file `.json` bạn đã tải về. Nội dung của nó sẽ là tất cả những gì bạn cần.
2.  Khi bạn triển khai ứng dụng Streamlit lên Streamlit Community Cloud (ở giai đoạn sau), hãy vào phần **Settings > Secrets**.
3.  Tạo một secret mới có tên là `gsheets` và dán **toàn bộ nội dung** của file `.json` vào đó. Ví dụ:
    ```toml
    [connections.gsheets]
    type = "streamlit_gsheets.GSheetsConnection"
    worksheet = "Feedback"
    # ... (phần còn lại của file JSON sẽ được Streamlit tự động xử lý)
    # Bạn chỉ cần dán toàn bộ nội dung file json vào secret
    ```
    **Cách đơn giản hơn:** Streamlit cho phép bạn dán trực tiếp nội dung file JSON vào secret, nó sẽ tự hiểu.

Bây giờ, ứng dụng Streamlit của bạn đã có thể ghi dữ liệu phản hồi một cách an toàn.
