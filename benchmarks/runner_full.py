"""
Comprehensive experiment runner:
- supports methods: FULL, SLERP, HMS
- supports inference backends: transformers, llama_cpp, vllm_http
- profiles memory/latency, computes scores (keyword/regex/code unit tests)
- produces JSON results and optional CSV/plots via report_generator
"""
import os
import json
import time
import argparse
from pathlib import Path

from utils import load_json, save_json, now_ts
from profiler import measure_peak_rss, start_gpu_vram_poller
from inference_backends import infer_with_transformers, infer_with_llama_cpp, infer_with_vllm_http
from scorers import keyword_scorer, regex_scorer, code_unit_test_scorer
from graph_router_bench import simple_graph_router

# merging implementations assumed present in merging/ or hms/
from merging.slerp import linear_merge
from hms.hms import HMSSynthesizer

def load_adapters_npz(paths):
    import numpy as np
    mats = []
    for p in paths:
        data = np.load(p)
        # heuristics: use first array in npz
        key = list(data.files)[0]
        mats.append(data[key])
    return mats

def run_one_experiment(cfg):
    out = {"config": cfg, "timestamp": now_ts()}
    method = cfg.get("method")
    use_gpu = cfg.get("use_gpu", False)
    gpu_poller = start_gpu_vram_poller() if use_gpu else (lambda: 0)

    # Merge step
    if method == "HMS":
        meta_list = cfg["meta_list"]
        prof = measure_peak_rss(lambda: HMSSynthesizer().synthesize(meta_list))
        merged_path = cfg.get("out_path", "bench/out_hms.npz")
        import numpy as np
        np.savez(merged_path, merged=prof["result"])
    elif method == "SLERP":
        adapters = cfg["adapters"]
        alphas = cfg.get("alphas", [1.0]*len(adapters))
        def do_slerp():
            arrs = load_adapters_npz(adapters)
            return linear_merge(arrs, alphas)
        prof = measure_peak_rss(do_slerp)
        merged_path = cfg.get("out_path", "bench/out_slerp.npz")
        import numpy as np
        np.savez(merged_path, merged=prof["result"])
    elif method == "FULL":
        # FULL merging requires model checkpoints; placeholder that should be replaced
        def do_full():
            # user must implement heavy merging and return merged model path / object
            return "FULL_MERGE_PLACEHOLDER"
        prof = measure_peak_rss(do_full)
        merged_path = cfg.get("out_path", "bench/out_full.npz")
    else:
        raise RuntimeError("Unknown merge method")

    gpu_peak = gpu_poller()

    out.update({
        "merge_time_s": prof["time_s"],
        "merge_peak_rss_mb": prof["peak_rss_mb"],
        "merge_peak_vram_mb": gpu_peak,
        "merged_path": merged_path
    })

    # Inference & scoring
    backend_cfg = cfg.get("inference", {})
    backend = backend_cfg.get("backend", "transformers")
    model = backend_cfg.get("model", None)
    adapter_for_backend = merged_path if method in ("HMS","SLERP") else None

    results = {}
    for bench_name, bench_path in cfg.get("benchsets", {}).items():
        bench = load_json(bench_path)
        total_score = 0
        total_possible = 0
        latencies = []
        domain_results = []
        for case in bench["tasks"]:
            prompt = case["input"]
            expected = case.get("expected_keywords", [])
            # optional unit test block
            unit_test = case.get("unit_test", None)
            t0 = time.perf_counter()
            if backend == "transformers":
                text, meta = infer_with_transformers(model, prompt, adapter_path=adapter_for_backend, device="cpu")
            elif backend == "llama_cpp":
                text, meta = infer_with_llama_cpp(backend_cfg.get("llama_bin","./main"), model, prompt)
            elif backend == "vllm_http":
                text, meta = infer_with_vllm_http(backend_cfg.get("endpoint"), prompt)
            else:
                text, meta = ("[no-backend]", {"backend": "none"})

            t1 = time.perf_counter()
            latencies.append(t1 - t0)

            # scoring strategy selection
            if unit_test:
                score_obj = code_unit_test_scorer(text, unit_test, timeout=case.get("timeout",5))
                passed = 1 if score_obj.get("passed") else 0
                total_score += passed
                total_possible += 1
                domain_results.append({"case": case["input"], "type": "unit", "score": passed, "detail": score_obj})
            else:
                # keyword scoring by default, fallback to regex if patterns provided
                patterns = case.get("regex_patterns", None)
                if patterns:
                    sc = regex_scorer(text, patterns)
                else:
                    sc = keyword_scorer(text, expected)
                total_score += sc["score"]
                total_possible += sc["total"]
                domain_results.append({"case": case["input"], "score_obj": sc, "output_preview": text[:400]})

        results[bench_name] = {
            "score": total_score,
            "possible": total_possible,
            "accuracy": (total_score / total_possible) if total_possible else 0.0,
            "latency_median_s": float(sorted(latencies)[len(latencies)//2]) if latencies else 0.0,
            "latency_p95_s": float(sorted(latencies)[int(len(latencies)*0.95)-1]) if latencies and len(latencies)>1 else (latencies[-1] if latencies else 0.0),
            "cases": domain_results
        }

    out["bench_results"] = results

    # Router ablation & confusion matrix
    # If routing set provided
    routing_set = cfg.get("routing_set")
    if routing_set:
        from router.router import SemanticRouter
        import numpy as np
        router = SemanticRouter()
        true_labels = []
        pred_labels = []
        lat_r = []
        for rcase in load_json(routing_set)["tasks"]:
            txt = rcase["input"]
            true = rcase.get("domain")
            t0 = time.perf_counter()
            pred, _ = router.route(txt)
            t1 = time.perf_counter()
            true_labels.append(true)
            pred_labels.append(pred)
            lat_r.append(t1-t0)
        out["routing"] = {
            "true": true_labels,
            "pred": pred_labels,
            "latency_median_s": float(sorted(lat_r)[len(lat_r)//2]) if lat_r else 0.0
        }

    return out

def run_experiments_file(experiments_json, out_dir="bench/results"):
    exps = load_json(experiments_json)
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for i, cfg in enumerate(exps):
        print(f"[RUN] {i+1}/{len(exps)} method={cfg.get('method')}")
        r = run_one_experiment(cfg)
        outpath = os.path.join(out_dir, f"exp_{i}_{r['config'].get('method')}_{now_ts()}.json")
        save_json(r, outpath)
        results.append(r)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exps", default="bench/experiments_full.json")
    parser.add_argument("--out", default="bench/results")
    args = parser.parse_args()
    run_experiments_file(args.exps, args.out)