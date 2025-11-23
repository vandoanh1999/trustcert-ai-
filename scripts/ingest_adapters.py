"""
Load adapter metadata + random embeddings into WeightIndex.
Use this after creating adapter_demo.npz for all experts.
"""

import json
import numpy as np
from weightindex.indexer import PersistentIndex

# Initialize the index. It will load if it exists.
index = PersistentIndex()

experts = [
    "adapters/expert_math/metadata.json",
    "adapters/expert_code/metadata.json",
    "adapters/expert_history/metadata.json"
]

print("Starting adapter ingestion...")
for path in experts:
    with open(path, "r") as f:
        meta = json.load(f)

    wid = meta["id"]

    # Use the real router's encoder to generate a semantic embedding
    # This makes the index much more realistic
    try:
        from router import SemanticRouter
        # A bit of a hack to get the encoder, but fine for a script
        encoder = SemanticRouter().encoder
        # Create an embedding from a descriptive text
        description = meta.get("description", wid)
        emb = encoder.encode(description, normalize_embeddings=True, convert_to_numpy=True)
    except Exception as e:
        print(f"Could not use semantic encoder ({e}), falling back to random embedding.")
        rng = np.random.default_rng(abs(hash(wid)) % (10**8))
        emb = rng.normal(0, 1, 384).astype("float32")
        emb /= (np.linalg.norm(emb) + 1e-9)

    index.add(wid, emb, meta)

# CRITICAL STEP: Save the index to disk after adding all adapters.
index.save()
index.close()

print("Ingest and save complete.")
