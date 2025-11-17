import os

# --- Biến môi trường chung ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
BASE_MODEL_NAME = os.getenv("BASE_MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
EMBEDDING_MODEL_DIM = int(os.getenv("EMBEDDING_MODEL_DIM", 384))

# --- Cấu hình Kết nối ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")

# --- Cấu hình Neo4j ---
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# --- Cấu hình API Gateway ---
API_KEY = os.getenv("API_KEY", "your_super_secret_api_key")

# --- Cấu hình Lưu trữ LoRA (S3/MinIO) ---
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# --- URL Dịch vụ Nội bộ ---
EMBEDDER_URL = "http://embedder:8002"
GRAPH_URL = "http://graph:8003"
ROUTER_URL = "http://router:8005"
TRAINER_URL = "http://trainer:8007"
