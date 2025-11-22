# run ingest: python3 scripts/ingest_weights.py
import sys
sys.path.append('src')
from src.demo import build_index_and_run_demo
build_index_and_run_demo()
