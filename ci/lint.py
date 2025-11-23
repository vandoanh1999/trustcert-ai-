"""
Simple static checks:
- file existence
- module importability
"""

import os
import importlib

required_paths = [
    "adapters",
    "router",
    "hms",
    "scripts",
    "benchmarks",
    "api",
    "weightindex"
]

missing = [p for p in required_paths if not os.path.exists(p)]

if missing:
    print("Missing directories:", missing)
else:
    print("All directories OK.")

modules = [
    "router.router",
    "router.shepherd_encoder",
    "hms.hms",
    "weightindex.indexer"
]

for m in modules:
    try:
        importlib.import_module(m)
        print("[OK]", m)
    except Exception as e:
        print("[ERR]", m, e)
