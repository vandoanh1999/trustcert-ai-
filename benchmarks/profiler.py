"""
Profiling helpers: peak RSS, GPU VRAM polling, latency measurement.
"""
import psutil
import time
import threading
import subprocess
import os

def measure_peak_rss(func, *args, **kwargs):
    proc = psutil.Process(os.getpid())
    peak = 0
    running = True

    def poll():
        nonlocal peak
        while running:
            try:
                mem = proc.memory_info().rss
                if mem > peak: peak = mem
            except Exception:
                pass
            time.sleep(0.01)

    t = threading.Thread(target=poll, daemon=True)
    t.start()
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    t1 = time.perf_counter()
    running = False
    t.join(timeout=1.0)
    return {
        "result": result,
        "time_s": t1 - t0,
        "peak_rss_mb": peak / (1024 * 1024)
    }

def start_gpu_vram_poller(interval=0.05):
    peak = 0
    running = True
    def poll():
        nonlocal peak
        while running:
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
                    stderr=subprocess.DEVNULL
                )
                lines = out.decode().strip().splitlines()
                for l in lines:
                    v = int(l.strip())
                    if v > peak: peak = v
            except Exception:
                pass
            time.sleep(interval)
    t = threading.Thread(target=poll, daemon=True)
    t.start()
    def stop():
        nonlocal running
        running = False
        t.join(timeout=1.0)
        return peak
    return stop

def timeit(func):
    def wrapper(*a, **k):
        t0 = time.perf_counter()
        r = func(*a, **k)
        t1 = time.perf_counter()
        return {"result": r, "time_s": t1 - t0}
    return wrapper