Bench directory - Enhanced runner
Files:
- utils.py                : helpers
- profiler.py             : memory & GPU profiling
- inference_backends.py   : transformers, llama.cpp, vLLM hooks
- scorers.py              : keyword/regex/unit-test scoring
- graph_router_bench.py   : simple GNN router simulation
- runner_full.py          : orchestration entrypoint
- experiments_full.json   : sample experiments
- report_generator.py     : CSV + plots
- benchmarks/*             : benchset json files (routing, code, math)
Usage:
1) Populate adapters / models as required
2) python3 -m bench.runner_full --exps bench/experiments_full.json
3) python3 bench/report_generator.py
Notes:
- For real LoRA/PEFT workflows supply adapters as PEFT dirs and transformers backend.
- For llama.cpp ensure binary path is correct in experiments file.