import sys
from unittest.mock import MagicMock

class MockTensor:
    def __init__(self, data=0.0, dtype=None, device=None):
        self.data = data
        self.device = device
    def detach(self): return self
    def cpu(self): return self
    def item(self): return self.data

torch = MagicMock()
torch.float32 = "float32"
torch.tensor = lambda data, dtype=None, device=None: MockTensor(data, dtype, device)
sys.modules["torch"] = torch
