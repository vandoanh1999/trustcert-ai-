"""
Persistent FAISS index + SQLite metadata store (V3 Production-Ready)

Refactored to separate add and save operations for efficiency.
"""

import faiss
import numpy as np
import sqlite3
import json
import os

class PersistentIndex:
    def __init__(self, dim=384, db_path="weights_meta.db", index_path="faiss.index"):
        self.dim = dim
        self.db_path = db_path
        self.index_path = index_path
        self._dirty = False  # Track if the index needs saving

        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._ensure_meta_table()

        if os.path.exists(self.index_path):
            print(f"Loading existing FAISS index from {self.index_path}")
            self.index = faiss.read_index(self.index_path)
        else:
            print("Creating new FAISS index.")
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dim))

        # Load existing IDs from DB to sync with FAISS index
        self._id_map = self._load_ids_from_db()
        # It's crucial that the number of items in the DB and Faiss index match.
        # A full production system would need a more robust sync/rebuild mechanism.
        if self.index.ntotal != len(self._id_map):
             print(f"Warning: FAISS index size ({self.index.ntotal}) and DB size ({len(self._id_map)}) mismatch. Consider rebuilding index.")


    def _ensure_meta_table(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS weights(
                         id TEXT PRIMARY KEY,
                         meta JSON,
                         faiss_id INTEGER UNIQUE
                     )""")
        self.conn.commit()

    def _load_ids_from_db(self):
        c = self.conn.cursor()
        c.execute("SELECT faiss_id, id FROM weights ORDER BY faiss_id ASC")
        return {faiss_id: str_id for faiss_id, str_id in c.fetchall()}

    def add(self, wid: str, emb: np.ndarray, meta: dict):
        """Adds a new adapter to the index in memory."""
        if wid in self._id_map.values():
            print(f"ID {wid} already exists. Skipping.")
            return

        emb = emb.astype("float32").reshape(1, -1)
        faiss.normalize_L2(emb)

        # Use a simple integer ID for FAISS
        new_faiss_id = self.index.ntotal
        self.index.add_with_ids(emb, np.array([new_faiss_id]))

        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO weights(id, meta, faiss_id) VALUES (?, ?, ?)",
            (wid, json.dumps(meta), new_faiss_id)
        )
        self.conn.commit()

        self._id_map[new_faiss_id] = wid
        self._dirty = True
        print(f"Added '{wid}' to index (in memory).")

    def save(self):
        """Saves the FAISS index to disk if changes have been made."""
        if self._dirty:
            print(f"Saving FAISS index to {self.index_path}...")
            faiss.write_index(self.index, self.index_path)
            self._dirty = False
            print("Save complete.")
        else:
            print("No changes to save.")

    def search(self, query_vec: np.ndarray, topk=5):
        """Searches the index for the most similar adapters."""
        q = query_vec.astype("float32").reshape(1, -1)
        faiss.normalize_L2(q)

        D, I = self.index.search(q, topk)

        results = []
        cur = self.conn.cursor()

        for dist, faiss_id in zip(D[0], I[0]):
            if faiss_id < 0: continue # Invalid ID

            str_id = self._id_map.get(faiss_id)
            if str_id:
                cur.execute("SELECT meta FROM weights WHERE id=?", (str_id,))
                row = cur.fetchone()
                if row:
                    results.append({
                        "id": str_id,
                        "similarity": float(dist),
                        "meta": json.loads(row[0])
                    })
        return results

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
