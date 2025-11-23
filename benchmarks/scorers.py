"""
Scoring utilities:
- keyword_scorer: counts presence of keywords
- regex_scorer: regex based evaluation
- code_unit_test_scorer: execute generated code in sandbox and run unit tests
- simple_fuzzy_scorer: token overlap / ratio
"""
import re
import tempfile
import os
import subprocess
import textwrap
import json
import uuid
import shutil

def keyword_scorer(output_text, expected_keywords):
    out = output_text or ""
    score = sum(1 for k in expected_keywords if k in out)
    return {"score": score, "total": len(expected_keywords)}

def regex_scorer(output_text, patterns):
    out = output_text or ""
    score = 0
    for p in patterns:
        if re.search(p, out):
            score += 1
    return {"score": score, "total": len(patterns)}

def code_unit_test_scorer(output_text, unit_test_code, timeout=5):
    """
    Build a temporary python file containing the user's function + unit tests,
    run it in subprocess with timeout. Unit test file should raise non-zero on failure,
    or print results. We'll capture returncode and stdout/stderr.
    Returns {"passed": bool, "rc": int, "stdout": str, "stderr": str}
    """
    tmpdir = tempfile.mkdtemp(prefix="code_eval_")
    try:
        func_file = os.path.join(tmpdir, "submission.py")
        test_file = os.path.join(tmpdir, "test_runner.py")

        # Write submission (the generated code)
        with open(func_file, "w", encoding="utf-8") as f:
            f.write(output_text)

        # Write test runner which imports submission and runs tests
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(textwrap.dedent(unit_test_code))

        # Run tests in an isolated process
        cmd = ["python3", test_file]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmpdir, text=True)
        try:
            out, err = proc.communicate(timeout=timeout)
            rc = proc.returncode
            passed = (rc == 0)
            return {"passed": passed, "rc": rc, "stdout": out, "stderr": err}
        except subprocess.TimeoutExpired:
            proc.kill()
            return {"passed": False, "rc": -9, "stdout": "", "stderr": "timeout"}
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

def fuzzy_token_overlap(output_text, reference_text, min_len=3):
    out_tokens = re.findall(r"\w+", output_text.lower())
    ref_tokens = re.findall(r"\w+", reference_text.lower())
    if not ref_tokens:
        return {"overlap": 0.0}
    inter = set(out_tokens) & set(ref_tokens)
    return {"overlap": len(inter) / max(1, len(set(ref_tokens)))}