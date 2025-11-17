import os

# --- Cấu hình Cloud ---
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

HF_TOKEN = os.getenv("HF_TOKEN")

# --- Cấu hình API Gateway ---
API_KEY = os.getenv("API_KEY", "your_super_secret_api_key")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Cấu hình Model & Dịch vụ ---
BASE_MODEL_NAME = os.getenv("BASE_MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
EMBEDDING_MODEL_DIM = int(os.getenv("EMBEDDING_MODEL_DIM", 384))

# URL Dịch vụ Nội bộ (sẽ được thay thế bằng các lệnh gọi trực tiếp hoặc API cloud)
EMBEDDER_URL = "http://embedder:8002"
GRAPH_URL = "http://graph:8003"
ROUTER_URL = "http://router:8005"
TRAINER_URL = "http://trainer:8007"
