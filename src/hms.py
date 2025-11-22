
import numpy as np
from .mmap_loader import load_hyper_tensors
def synthesize(hyper_uris, alphas=None):
    if alphas is None:
        alphas = [1.0]*len(hyper_uris)
    acc = None
    total_alpha = sum(alphas) if sum(alphas)!=0 else 1.0
    for uri, a in zip(hyper_uris, alphas):
        comp = load_hyper_tensors(uri)
        t = None
        for v in comp.values():
            t = np.array(v)
            break
        if t is None:
            continue
        if acc is None:
            acc = a * t.astype('float32')
        else:
            acc += a * t.astype('float32')
    if acc is None:
        return None
    return (acc / total_alpha).astype('float32')
