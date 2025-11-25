# Makefile for Genesis Core V7 - The Symbiotic Network

.PHONY: help install setup run demo ci

help:
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup      - Run the initial setup script to create dummy data"
	@echo "  run        - Run the main FastAPI server for the V7 API"
	@echo "  demo       - Run the Streamlit UI for the Genesis Hub"
	@echo "  ci         - Run the V7 integration self-test"

install:
	pip install -r requirements.txt

setup:
	bash setup.sh

run:
	uvicorn api.main:app --host 0.0.0.0 --port 8000

demo:
	streamlit run frontend/app.py

ci:
	python3 ci/selftest.py
