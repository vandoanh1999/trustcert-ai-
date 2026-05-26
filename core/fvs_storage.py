# core/fvs_storage.py - FAISS Vector Store (Thay the Qdrant)
import faiss
import numpy as np
import sqlite3
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class FaissVectorStore:
    """
    Local Vector Store using FAISS
    - Replaces Qdrant Cloud ($0 cost)
    - Supports millions of vectors
    - Disk persistence
    """
    
    def __init__(self, node_id: str, dimension: int = 384, 
                 data_dir: str = "./data/fvs", index_type: str = "Flat"):
        self.node_id = node_id
        self.dimension = dimension
        
        # Paths
        self.data_dir = Path(data_dir) / node_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.data_dir / "faiss.index"
        self.db_path = self.data_dir / "metadata.db"
        
        # Initialize FAISS index
        if index_type == "Flat":
            self.index = faiss.IndexFlatIP(dimension)
        elif index_type == "IVF":
            nlist = 100
            quantizer = faiss.IndexFlatIP(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            self.index.nprobe = 10
        
        # Load existing index
        if self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")
        
        # Metadata DB
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()
        
        # Vector ID mapping
        self.vector_ids = self._load_vector_ids()
        self.vector_ids_set = set(self.vector_ids)
        
        logger.info(f"FVS initialized: {node_id} ({len(self.vector_ids)} vectors)")
    
    def _init_db(self):
        """Initialize metadata database"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                idx INTEGER PRIMARY KEY,
                id TEXT UNIQUE NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT,
                timestamp INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_id ON vectors(id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON vectors(timestamp)")
        self.conn.commit()
    
    def _load_vector_ids(self) -> List[str]:
        """Load vector IDs from DB"""
        cursor = self.conn.execute("SELECT id FROM vectors ORDER BY idx")
        return [row[0] for row in cursor]
    
    def save(self, text: str, embedding: np.ndarray, 
             vec_id: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """Save vector to store"""
        # Generate ID if not provided
        if not vec_id:
            vec_id = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        # BOLT OPTIMIZATION: O(1) duplicate check using set
        if vec_id in self.vector_ids_set:
            logger.debug(f"Vector exists: {vec_id}")
            return vec_id
        
        # Normalize embedding
        embedding = embedding.astype('float32')
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        # Add to FAISS
        idx = self.index.ntotal
        self.index.add(embedding.reshape(1, -1))
        
        # Save metadata
        self.conn.execute("""
            INSERT INTO vectors (idx, id, text, metadata)
            VALUES (?, ?, ?, ?)
        """, (idx, vec_id, text, str(metadata) if metadata else None))

        # BOLT OPTIMIZATION: Batch commits to persist_index and close to avoid I/O bottleneck
        # self.conn.commit()
        
        self.vector_ids.append(vec_id)
        self.vector_ids_set.add(vec_id)
        
        # Persist index every 100 vectors
        if idx % 100 == 0:
            self._persist_index()
        
        logger.debug(f"Saved vector: {vec_id}")
        return vec_id
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query
        query = query_embedding.astype('float32')
        norm = np.linalg.norm(query)
        if norm > 0:
            query = query / norm
        
        # FAISS search
        scores, indices = self.index.search(query.reshape(1, -1), min(top_k, self.index.ntotal))
        
        # BOLT OPTIMIZATION: Batched metadata retrieval to solve N+1 query problem
        valid_indices = [int(idx) for idx in indices[0] if idx != -1]
        if not valid_indices:
            return []

        placeholders = ','.join(['?'] * len(valid_indices))
        query_sql = f"SELECT idx, id, text, metadata FROM vectors WHERE idx IN ({placeholders})"
        cursor = self.conn.execute(query_sql, valid_indices)

        # Map results to preserve FAISS score ordering
        metadata_map = {row[0]: row for row in cursor.fetchall()}

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx not in metadata_map:
                continue
            
            row = metadata_map[idx]
            results.append({
                "id": row[1],
                "text": row[2],
                "metadata": row[3],
                "score": float(score)
            })
        
        return results
    
    def _persist_index(self):
        """Save index to disk"""
        try:
            # BOLT OPTIMIZATION: Commit SQLite transactions when persisting FAISS index
            self.conn.commit()
            faiss.write_index(self.index, str(self.index_path))
            logger.debug("Index persisted to disk")
        except Exception as e:
            logger.error(f"Failed to persist index: {e}")
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        idx_size = self.index_path.stat().st_size if self.index_path.exists() else 0
        
        return {
            "node_id": self.node_id,
            "total_vectors": self.index.ntotal,
            "storage_mb": (db_size + idx_size) / (1024 * 1024),
            "dimension": self.dimension
        }
    
    def close(self):
        """Cleanup"""
        self._persist_index()
        self.conn.close()