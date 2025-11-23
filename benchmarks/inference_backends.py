"""
Inference backend wrappers.
- Transformers (HuggingFace + PEFT) backend (if available)
- llama.cpp subprocess backend (if installed locally)
- vLLM placeholder (requires vllm server integration)
Each function returns (text_output, meta_dict)
"""
import os
import json
import tempfile
import subprocess
import time

def infer_with_transformers(model_name, prompt, adapter_path=None, max_new_tokens=128, device="cpu"):
    """
    Attempt to use transformers + peft to load base model and apply adapter (if adapter_path given as npz).
    This is best-effort: requires transformers, accelerate, peft installed and compatible model.
    Returns (output_text, meta).
    """
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        # PEFT application of an adapter file in npz is non-trivial; we expect adapter_path could be a PEFT dir.
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if device.startswith("cuda") else torch.float32, low_cpu_mem_usage=True)
        if adapter_path:
            try:
                # try to load peft adapter folder
                from peft import PeftModel
                model = PeftModel.from_pretrained(model, adapter_path)
            except Exception:
                # fallback: no adapter applied
                pass
        model.eval()
        if device.startswith("cuda"):
            model.to(device)
        inputs = tokenizer(prompt, return_tensors="pt").to(next(model.parameters()).device)
        with torch.no_grad():
            gen = model.generate(**inputs, max_new_tokens=max_new_tokens)
        out = tokenizer.decode(gen[0], skip_special_tokens=True)
        meta = {"backend": "transformers", "model": model_name}
        return out, meta
    except Exception as e:
        return f"[transformers backend error] {e}", {"backend": "transformers", "error": str(e)}

def infer_with_llama_cpp(llama_bin, model_path, prompt, max_tokens=128, timeout=30):
    """
    Calls llama.cpp or compatible CLI to run inference.
    Expects a binary (llama.cpp CLI wrapper) that accepts model path and prompt.
    Returns (output_text, meta)
    Example command expected: ./main -m model.bin -p "prompt" -n 128
    """
    cmd = [llama_bin, "-m", model_path, "-p", prompt, "-n", str(max_tokens)]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        out = p.stdout.strip()
        if not out:
            out = p.stderr.strip()
        return out, {"backend": "llama_cpp", "model": model_path, "rc": p.returncode}
    except Exception as e:
        return f"[llama_cpp error] {e}", {"backend": "llama_cpp", "error": str(e)}

def infer_with_vllm_http(endpoint_url, prompt, max_tokens=128):
    """
    POST to vLLM HTTP infer endpoint (user must run vllm server separately).
    Expects endpoint like http://host:port/generate
    """
    try:
        import requests
        payload = {"prompt": prompt, "max_tokens": max_tokens}
        r = requests.post(endpoint_url, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json().get("text", ""), {"backend": "vllm_http", "url": endpoint_url}
        else:
            return f"[vllm_http error] status {r.status_code}", {"backend": "vllm_http", "status": r.status_code, "text": r.text}
    except Exception as e:
        return f"[vllm_http error] {e}", {"backend": "vllm_http", "error": str(e)}