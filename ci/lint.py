"""
V3 Linter: Simple static checks for the Genesis Core V3 architecture.
- directory existence
- module importability
"""

import os
import importlib
import sys

# Ensure the root directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("--- Running V3 Linter ---")

has_error = False

# 1. Check for required directories
required_paths = [
    "adapters",
    "router",
    "synthesizer", # <-- Replaced hms
    "merging",     # <-- Added merging
    "scripts",
    "benchmarks",
    "api",
    "weightindex",
    "ci",
    "docs"
]
print("\nChecking for required directories...")
missing = [p for p in required_paths if not os.path.exists(p)]

if missing:
    print(f"[FAIL] Missing directories: {missing}")
    has_error = True
else:
    print("[OK] All required directories exist.")

# 2. Check for critical module importability
modules_to_check = [
    "router.router",
    "synthesizer.main", # <-- Replaced hms.hms
    "weightindex.indexer",
    "merging.slerp",
    "api.server"
]
print("\nChecking for critical module importability...")
for m in modules_to_check:
    try:
        importlib.import_module(m)
        print(f"[OK]   Module '{m}' can be imported.")
    except Exception as e:
        print(f"[FAIL] Module '{m}' failed to import: {e}")
        has_error = True

print("\n--- Linter Run Complete ---")
if has_error:
    print("Linter found errors.")
    sys.exit(1)
else:
    print("Linter passed successfully.")
