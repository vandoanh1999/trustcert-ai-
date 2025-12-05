# Makefile for Genesis Core V7 - The Symbiotic Network

.PHONY: help install setup run demo ci

help:
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup      - Run the initial setup script to create dummy data"
	@echo "  run        - Run the main FastAPI server for the V8 API"
	@echo "  demo       - Run the Streamlit UI for the Genesis Hub"
	@echo "  dashboard  - Run the live network monitoring dashboard"
	@echo "  ci         - Run all V8 integration self-tests"

install:
	pip install -r requirements.txt

setup:
	bash setup.sh

run:
	uvicorn api.main:app --host 0.0.0.0 --port 8000

demo:
	streamlit run frontend/app.py

dashboard:
	streamlit run frontend/dashboard.py

ci:
	@echo "--- Running V8 Core Security Self-Test ---"
	python3 core/security.py
	@echo "\n--- Running V8 Decentralized Network Self-Test ---"
	python3 ci/v8_decentralized_test.py
	@echo "\n--- Running V8 Anti-Sybil Self-Test ---"
	python3 ci/v8_sybil_test.py
	@echo "\n--- All Tests Passed! ---"
