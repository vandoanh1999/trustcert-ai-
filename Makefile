# Makefile for Genesis Core V2

.PHONY: help install run ingest demo bench ci setup

help:
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup      - Run the initial setup script to create demo adapters"
	@echo "  run        - Run the FastAPI server"
	@echo "  ingest     - Ingest adapters into the WeightIndex"
	@echo "  demo       - Run the full pipeline demo"
	@echo "  bench      - Run the benchmarks"
	@echo "  ci         - Run the full CI pipeline"

install:
	pip install -r requirements.txt

setup:
	bash setup.sh

run:
	uvicorn api.server:app --host 0.0.0.0 --port 8000

ingest:
	python3 scripts/ingest_adapters.py

demo:
	python3 scripts/run_demo.py

bench:
	python3 benchmarks/run_benchmarks.py

ci:
	bash ci/run_full_pipeline.sh
