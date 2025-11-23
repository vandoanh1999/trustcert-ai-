#!/bin/bash

echo "[1] Ingesting adapters..."
python3 scripts/ingest_adapters.py

echo "[2] Running merge tests..."
python3 scripts/merge_test.py

echo "[3] Running benchmarks..."
python3 benchmarks/run_benchmarks.py

echo "[ OK ] CI pipeline completed."
