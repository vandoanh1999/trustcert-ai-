#!/bin/bash

# This script sets up the initial environment for Genesis Core V2
# by creating valid dummy adapters and ingesting them.

echo "[*] Creating directories for demo adapters..."
mkdir -p adapters/expert_math adapters/expert_code adapters/expert_history

echo "[*] Creating demo adapter metadata files..."
cat <<EOF > adapters/expert_math/metadata.json
{
  "id": "expert_math_v1",
  "domain": "math",
  "description": "Expert adapter for mathematical reasoning.",
  "address": "math_adapter_loc",
  "tensor_components": 3,
  "trust_score": 0.95
}
EOF

cat <<EOF > adapters/expert_code/metadata.json
{
  "id": "expert_code_v1",
  "domain": "code",
  "description": "Expert adapter for Python code generation.",
  "address": "code_adapter_loc",
  "tensor_components": 4,
  "trust_score": 0.92
}
EOF

cat <<EOF > adapters/expert_history/metadata.json
{
  "id": "expert_history_v1",
  "domain": "history",
  "description": "Expert adapter for historical facts.",
  "address": "history_adapter_loc",
  "tensor_components": 2,
  "trust_score": 0.88
}
EOF

echo "[*] Creating VALID dummy tensor files for demo adapters..."
# Use python to create small but valid safetensors files
python3 -c "
import numpy as np
from safetensors.numpy import save_file
import os

files_to_create = {
    'adapters/expert_math/adapter.safetensors': {'layer1': np.random.rand(16,32).astype('float32')},
    'adapters/expert_code/adapter.safetensors': {'layer1': np.random.rand(16,32).astype('float32')},
    'adapters/expert_history/adapter.safetensors': {'layer1': np.random.rand(16,32).astype('float32')}
}

for path, tensors in files_to_create.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    save_file(tensors, path)
    print(f'  - Created {path}')
"

echo "[*] Ingesting adapters into the WeightIndex..."
# Make sure PYTHONPATH is set so scripts can find modules
export PYTHONPATH=.
python3 scripts/ingest_adapters.py

echo "[*] Setup complete. You can now run the demo or start the server."
