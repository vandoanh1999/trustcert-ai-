"""
Takes JSON results produced by runner_full and generates CSV + plots:
- merge_time comparison
- peak memory comparison
- per-domain accuracy bar chart
- routing confusion matrix heatmap
"""
import os
import json
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def load_results(folder="bench/results"):
    files = glob.glob(os.path.join(folder, "*.json"))
    datas = [json.load(open(f,"r",encoding="utf-8")) for f in files]
    return datas

def results_to_csv(results, out_csv="bench/summary.csv"):
    rows = []
    for r in results:
        cfg = r.get("config",{})
        rows.append({
            "method": cfg.get("method"),
            "merge_time_s": r.get("merge_time_s"),
            "merge_peak_rss_mb": r.get("merge_peak_rss_mb"),
            "merge_peak_vram_mb": r.get("merge_peak_vram_mb"),
            "math_accuracy": r.get("bench_results",{}).get("math",{}).get("accuracy"),
            "code_accuracy": r.get("bench_results",{}).get("code",{}).get("accuracy")
        })
    keys = rows[0].keys() if rows else []
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(keys))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return out_csv

def plot_accuracy_bar(results, out_png="bench/accuracy_bar.png"):
    methods = []
    math_scores = []
    code_scores = []
    for r in results:
        methods.append(r.get("config",{}).get("method"))
        math_scores.append(r.get("bench_results",{}).get("math",{}).get("accuracy",0))
        code_scores.append(r.get("bench_results",{}).get("code",{}).get("accuracy",0))
    x = np.arange(len(methods))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar(x - width/2, math_scores, width, label="math")
    ax.bar(x + width/2, code_scores, width, label="code")
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel("Accuracy")
    ax.set_title("Per-method Accuracy")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_png)
    return out_png

def plot_merge_memory(results, out_png="bench/memory_bar.png"):
    methods = []
    mem = []
    for r in results:
        methods.append(r.get("config",{}).get("method"))
        mem.append(r.get("merge_peak_rss_mb",0))
    x = np.arange(len(methods))
    fig, ax = plt.subplots()
    ax.bar(x, mem)
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylabel("Peak RSS (MB)")
    ax.set_title("Merge Peak Memory by Method")
    plt.tight_layout()
    plt.savefig(out_png)
    return out_png

def plot_routing_confusion(results, out_png="bench/routing_confusion.png"):
    # collect last result with routing
    for r in results:
        if r.get("routing"):
            true = r["routing"]["true"]
            pred = r["routing"]["pred"]
            labels = sorted(list(set(true + pred)))
            cm = confusion_matrix(true, pred, labels=labels)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
            fig, ax = plt.subplots(figsize=(6,6))
            disp.plot(ax=ax)
            plt.title("Routing Confusion Matrix")
            plt.tight_layout()
            plt.savefig(out_png)
            return out_png
    return None

if __name__ == "__main__":
    res = load_results()
    results_to_csv(res)
    plot_accuracy_bar(res)
    plot_merge_memory(res)
    plot_routing_confusion(res)