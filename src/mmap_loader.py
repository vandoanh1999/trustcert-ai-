
import os, numpy as np
try:
    from safetensors.numpy import load_file as safetensors_load_np
    HAVE_SAFETENS = True
except Exception:
    HAVE_SAFETENS = False
def get_local_path_or_fail(uri, local_dir='weights_cache'):
    os.makedirs(local_dir, exist_ok=True)
    fn = os.path.basename(uri)
    path = os.path.join(local_dir, fn)
    if os.path.exists(path):
        return path
    raise FileNotFoundError(f'Local weight not found: {path}')
def load_hyper_tensors(uri):
    path = get_local_path_or_fail(uri)
    if HAVE_SAFETENS and path.endswith('.safetensors'):
        data = safetensors_load_np(path)
        return data
    elif path.endswith('.npz'):
        data = np.load(path, allow_pickle=True)
        return dict(data)
    elif path.endswith('.pt') or path.endswith('.pth'):
        import torch
        sd = torch.load(path, map_location='cpu')
        return {k: v.cpu().numpy() if hasattr(v, 'cpu') else np.array(v) for k,v in sd.items()}
    else:
        raise RuntimeError('Unsupported weight format: '+path)
