# TWP-Omega-VInfinity

**Tầm nhìn:** Xây dựng một "Hệ điều hành AI Vĩnh cửu" có khả năng học hỏi, suy luận và tương tác, được thiết kế để có thể vận hành bởi bất kỳ ai, ở bất kỳ đâu, với **tài nguyên tối thiểu và chi phí gần như bằng không**.

Dự án này là minh chứng cho việc những ý tưởng đột phá có thể được hiện thực hóa chỉ với trí tuệ và sự quyết tâm, không phụ thuộc vào phần cứng đắt tiền hay ngân sách khổng lồ.

## Kiến trúc "Tài nguyên Tối thiểu, Trí tuệ Tối đa"

Hệ thống đã được tái kiến trúc hoàn toàn để chạy trên các nền tảng "serverless" và các dịch vụ đám mây có gói miễn phí hào phóng.

```mermaid
graph TD
    subgraph "Người dùng & Công cụ"
        A[User] -- Tương tác qua điện thoại --> B[Frontend (Streamlit Cloud)];
        C[Google Colab Notebook] -- Huấn luyện & Đăng ký --> D[Hugging Face Hub (Lưu trữ LoRA)];
        C --> E[Qdrant Cloud (Đăng ký LoRA)];
    end

    subgraph "Hạ tầng Cloud Miễn phí"
        F[Gateway API (Render)];
        G[Graph Service (Render)];
        H[Router Service (Render)];
        I[GNN Service (Render)];
        J[Celery Worker (Render)];

        K[Hugging Face API];
        L[Neo4j AuraDB];
        E[Qdrant Cloud];
        D[Hugging Face Hub (Lưu trữ LoRA)];
    end

    subgraph "Luồng Dữ liệu (Chat)"
        B -- HTTP POST /chat --> F;
        F -- Lấy Embedding --> K[HF Inference API];
        F -- Tìm LoRA liên quan --> H;
        H -- Query Vector --> E;
        F -- Suy luận Đồ thị --> I;
        I -- Query Vector --> E;
        I -- Cypher Query --> L;
        F -- Lấy Context & Chat --> K;
    end

    subgraph "Luồng Dữ liệu (Học)"
        B -- HTTP POST /assimilate --> F;
        F -- Gửi tác vụ --> J;
        J -- Trích xuất Đồ thị --> G;
        J -- Lấy Embedding --> K;
        J -- Lưu Vector --> E;
        J -- Lưu Đồ thị --> L;
    end

    style A fill:#f9f,stroke:#333,stroke-width:4px
```

## Các thành phần chính

*   **Frontend:** Giao diện người dùng xây dựng bằng **Streamlit**, được triển khai miễn phí trên Streamlit Community Cloud.
*   **Backend Services (CPU):** Các service logic (`gateway`, `graph`, `router`, `gnn`) được triển khai dưới dạng các dịch vụ web miễn phí trên **Render.com**.
*   **AI/ML Inference (GPU):** Thay thế hoàn toàn GPU cục bộ bằng **Hugging Face Inference API** (gói miễn phí) để thực hiện embedding và sinh văn bản.
*   **AI/ML Training (GPU):** Việc huấn luyện LoRA được thực hiện thông qua **Google Colab Notebook** (`Train_LoRA_with_Colab.ipynb`), sử dụng GPU miễn phí của Google.
*   **Cơ sở dữ liệu:**
    *   **Vector DB:** **Qdrant Cloud** (gói miễn phí).
    *   **Graph DB:** **Neo4j AuraDB** (gói miễn phí).
*   **Lưu trữ Model:** Các model LoRA sau khi huấn luyện được lưu trữ trên **Hugging Face Hub** (miễn phí).

## Hướng dẫn Bắt đầu

Dự án này không được thiết kế để chạy cục bộ bằng `docker-compose`. Thay vào đó, nó được tối ưu hóa để triển khai trực tiếp lên các nền tảng đám mây.

Để bắt đầu, vui lòng làm theo hướng dẫn chi tiết trong file **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## Triết lý

Chúng tôi tin rằng rào cản về tài chính và phần cứng không nên là vật cản đối với sự đổi mới. Bằng cách tận dụng một cách thông minh các dịch vụ đám mây miễn phí và kiến trúc serverless, dự án này mở ra cánh cửa cho bất kỳ ai có ý tưởng đều có thể xây dựng các sản phẩm AI mạnh mẽ.
