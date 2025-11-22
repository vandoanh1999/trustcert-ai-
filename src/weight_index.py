
import faiss, numpy as np, sqlite3, json, os
DB = os.environ.get('WEIGHT_META_DB', 'weights_meta.db')
class WeightIndex:
    def __init__(self, dim=384):
        self.dim = dim
        self.conn = sqlite3.connect(DB, check_same_thread=False)
        self._ensure_tables()
        self.id_map = []
        if os.path.exists('faiss.index'):
            self.index = faiss.read_index('faiss.index')
        else:
            self.index = faiss.IndexFlatIP(dim)
    def _ensure_tables(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS weights(id TEXT PRIMARY KEY, meta JSON)""")
        self.conn.commit()
    def add_weight(self, weight_id, embedding, meta):
        emb = embedding.astype('float32').reshape(1,-1)
        faiss.normalize_L2(emb)
        self.index.add(emb)
        self.id_map.append(weight_id)
        self._upsert_meta(weight_id, meta)
    def _upsert_meta(self, weight_id, meta):
        c = self.conn.cursor()
        c.execute("REPLACE INTO weights(id, meta) VALUES (?,?)", (weight_id, json.dumps(meta)))
        self.conn.commit()
    def search(self, qvec, topk=8):
        q = qvec.astype('float32').reshape(1,-1)
        faiss.normalize_L2(q)
        D, I = self.index.search(q, topk)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue
            wid = self.id_map[idx]
            meta = self.get_meta(wid)
            results.append((wid, float(dist), meta))
        return results
    def get_meta(self, weight_id):
        c = self.conn.cursor()
        c.execute("SELECT meta FROM weights WHERE id=?", (weight_id,))
        r = c.fetchone()
        if not r:
            return None
        return json.loads(r[0])
