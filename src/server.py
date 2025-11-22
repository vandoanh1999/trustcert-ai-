
from fastapi import FastAPI
from pydantic import BaseModel
import os
from .shepherd import shepherd_embed
from .weight_index import WeightIndex
from .hms import synthesize
from .l4_dispatcher import l4_route
from .verifier import adaptive_verify
app = FastAPI()
WI = WeightIndex(dim=384)
class Query(BaseModel):
    text: str
    session_id: str = 'default'
@app.post('/dispatch')
async def dispatch(q: Query):
    qv = shepherd_embed(q.text)
    results = WI.search(qv, topk=4)
    chosen_ids = [r[0] for r in results]
    hyper_uris = [os.path.join('examples','sample_weights', r[0]) for r in results]
    try:
        adapter = synthesize(hyper_uris)
    except Exception:
        adapter = None
    route = l4_route(q.text)
    out = {'out': f'Executed by {route}', 'output_complexity': 10000}
    v = adaptive_verify(out, 'math' if '\\sum' in q.text else 'general')
    return {'chosen': chosen_ids, 'route': route, 'verify_score': v, 'out': out}
