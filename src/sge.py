
import time, uuid
def spawn_expert(parent_meta, seed_uris, max_steps=50):
    new_id = f"{parent_meta.get('id','parent')}_child_{uuid.uuid4().hex[:8]}"
    provisional = {'id': new_id, 'parent': parent_meta.get('id'), 'seeds': seed_uris, 'status':'provisional'}
    for i in range(min(max_steps, 50)):
        time.sleep(0.01)
    provisional['status'] = 'ready_for_review'
    return provisional
