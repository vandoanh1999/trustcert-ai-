import numpy as np
from core.fvs_storage import FaissVectorStore
import os
import shutil
import unittest

class TestFvsCorrectness(unittest.TestCase):
    def setUp(self):
        self.node_id = "test_node_correctness"
        self.dimension = 384
        if os.path.exists(f"./data/fvs/{self.node_id}"):
            shutil.rmtree(f"./data/fvs/{self.node_id}")
        self.fvs = FaissVectorStore(node_id=self.node_id, dimension=self.dimension)

    def tearDown(self):
        self.fvs.close()
        if os.path.exists(f"./data/fvs/{self.node_id}"):
            shutil.rmtree(f"./data/fvs/{self.node_id}")

    def test_search_order_and_metadata(self):
        # Create 10 vectors with known properties
        for i in range(10):
            # Create orthogonal vectors
            vec = np.zeros(self.dimension).astype('float32')
            vec[i] = 1.0
            self.fvs.save(text=f"doc_{i}", embedding=vec, vec_id=f"id_{i}", metadata={"val": i})

        # Query biased towards id_0, id_1, id_2...
        query = np.zeros(self.dimension).astype('float32')
        for i in range(10):
            query[i] = 1.0 / (i + 1)

        results = self.fvs.search(query, top_k=5)

        self.assertEqual(len(results), 5)
        # Should be ordered by doc index (0, 1, 2, 3, 4)
        for i in range(5):
            self.assertEqual(results[i]['id'], f"id_{i}")
            self.assertEqual(results[i]['text'], f"doc_{i}")
            # SQLite stores metadata as string representation of dict
            self.assertIn(f"'val': {i}", results[i]['metadata'])
            if i > 0:
                self.assertGreater(results[i-1]['score'], results[i]['score'])

    def test_search_empty(self):
        query = np.random.rand(self.dimension).astype('float32')
        results = self.fvs.search(query, top_k=5)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
