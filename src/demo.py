
import os, numpy as np, time
from .shepherd import shepherd_embed
from .weight_index import WeightIndex
from .hms import synthesize
from .l4_dispatcher import l4_route
from .verifier import adaptive_verify
def ingest_sample_weights(index: WeightIndex):
    sample_dir = os.path.join(os.path.dirname(__file__), '..', 'examples', 'sample_weights')
    files = [f for f in os.listdir(sample_dir) if f.endswith('.npz') or f.endswith('.safetensors') or f.endswith('.pt')]
    for fn in files:
        path = os.path.join(sample_dir, fn)
        emb = np.random.RandomState(abs(hash(fn)) % 2**32).randn(index.dim).astype('float32')
        meta = {'id': fn, 'uri': fn, 'tags':['demo'], 'vram_bytes': 1000000}
        index.add_weight(fn, emb, meta)
    print(f'Ingested {len(files)} sample weights into index.')
def build_index_and_run_demo():
    print('Building demo index...')
    idx = WeightIndex(dim=384)
    ingest_sample_weights(idx)
    sample_inputs = [
        "Prove that \sum_{n=1}^\infty 1/n^2 = pi^2/6 using analytic continuation",
        "Solve and simplify the algebraic expression: (x^2-1)/(x-1)",
        ">seq1\nATGCGTACGTAGCTAGCTAGCTAGCTA... (long fasta)"
    ]
    for text in sample_inputs:
        qv = shepherd_embed(text)
        results = idx.search(qv, topk=3)
        print('\n---\nQuery:', text[:120])
        chosen = [r[0] for r in results]
        hyper_uris = [os.path.join('examples','sample_weights', r[0]) for r in results]
        adapter = None
        try:
            adapter = synthesize(hyper_uris)
        except Exception as e:
            adapter = None
        print('Chosen weights:', chosen)
        if adapter is None:
            print('Synthesis failed: ensure sample weights exist in examples/sample_weights.')
            continue
        route = l4_route(text)
        result = {'out': f'Executed by {route}', 'output_complexity': int(1000 + adapter.size if hasattr(adapter, 'size') else 10000)}
        v = adaptive_verify(result, 'math' if '\\sum' in text else 'general')
        print('Route:', route, 'Verify score:', v)
    print('\nDemo finished.')
if __name__=='__main__':
    build_index_and_run_demo()
