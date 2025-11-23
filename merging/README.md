Merging module
==============

Contents:
- utils.py            : helpers for shape checks and weighted sums
- slerp.py            : linear and spherical interpolation helpers
- fisher.py           : fisher-weighted merge using diagonal fisher estimate
- procrustes.py       : orthogonal Procrustes alignment for matrices
- ties_sketch.py      : research scaffold for TIES-style merging
- __init__.py

Usage notes:
- For adapter-level merging (LoRA/adapters), prefer linear_merge(slerp.linear_merge) on the small adapter tensors.
- For weight-space merging on full model matrices, perform layer-wise alignment (procrustes), optionally fisher-weighted merge if fisher diagonals are available.
- Always keep backups and run benchmarks after merging.
