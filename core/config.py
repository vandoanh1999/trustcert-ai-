# core/config.py - Configuration Settings
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """Application settings with FVS P2P support"""
    
    # ============================================
    # FVS P2P Configuration (NEW)
    # ============================================
    ENABLE_FVS: bool = True
    FVS_NODE_ID: Optional[str] = None
    FVS_P2P_PORT: int = 8765
    FVS_IS_ANCHOR: bool = False
    FVS_BOOTSTRAP_MODE: str = "community"
    FVS_BOOTSTRAP_PEERS: str = ""
    FVS_RELAY_NODES: str = ""
    FVS_DATA_DIR: str = "./data/fvs"
    
    # ============================================
    # AI Models
    # ============================================
    HF_TOKEN: Optional[str] = None
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_MODEL_DIM: int = 384
    BASE_MODEL_NAME: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    # ============================================
    # API Security
    # ============================================
    API_KEY: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # ============================================
    # Legacy Cloud (Fallback - Optional)
    # ============================================
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    NEO4J_URI: Optional[str] = None
    NEO4J_USER: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "allow"
    
    def get_bootstrap_peers(self) -> List[str]:
        """Parse bootstrap peers from env"""
        if not self.FVS_BOOTSTRAP_PEERS:
            return []
        return [p.strip() for p in self.FVS_BOOTSTRAP_PEERS.split(",") if p.strip()]
    
    def get_relay_nodes(self) -> List[tuple]:
        """Parse relay nodes from env"""
        if not self.FVS_RELAY_NODES:
            return []
        nodes = []
        for node in self.FVS_RELAY_NODES.split(","):
            if ":" in node:
                ip, port = node.strip().split(":")
                nodes.append((ip, int(port)))
        return nodes

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()