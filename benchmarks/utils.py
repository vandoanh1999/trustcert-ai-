"""
Utility helpers used by bench suite.
"""
import os
import json
import time
import tempfile
import subprocess
from pathlib import Path

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def now_ts():
    return time.strftime("%Y%m%dT%H%M%S", time.gmtime())

def run_subprocess(cmd, timeout=30, capture_output=True):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out, err
    except subprocess.TimeoutExpired:
        proc.kill()
        return -9, "", "timeout"