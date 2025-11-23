"""
Genesis Core V3: Architecture-Aware Synthesizer

This is the new heart of the system, replacing the simplistic HMS module.
Its responsibilities:
- Load multiple real adapter models from `.safetensors` files.
- Treat the layers of these models as lists of matrices.
- Use advanced merging algorithms from the `merging` module to synthesize a new model.
"""

import numpy as np
from safetensors.numpy import load_file, save_file
from merging.ties_sketch import ties_simple_synthesize
from typing import List, Dict

class Synthesizer:
    def __init__(self):
        pass

    def _load_adapter(self, file_path: str) -> List[np.ndarray]:
        """Loads all tensors from a .safetensors file and returns them as a list."""
        try:
            tensors = load_file(file_path)
            # Return tensors in a consistent order, sorted by key
            return [tensors[key] for key in sorted(tensors.keys())]
        except Exception as e:
            print(f"Error loading adapter {file_path}: {e}")
            return []

    def synthesize(self, adapter_paths: List[str], alphas: List[float] = None) -> Dict[str, np.ndarray] | None:
        """
        Synthesizes a new model from a list of adapter file paths.

        Args:
            adapter_paths: A list of file paths to the .safetensors adapters.
            alphas: A list of weights for each adapter.

        Returns:
            A dictionary representing the new synthesized model's state_dict,
            or None if synthesis fails.
        """
        if not adapter_paths:
            raise ValueError("No adapter paths provided for synthesis.")

        # Load all models into a list of layer lists
        all_models_layers = [self._load_adapter(path) for path in adapter_paths]

        # Filter out any models that failed to load
        all_models_layers = [m for m in all_models_layers if m]
        if not all_models_layers:
            print("Could not load any valid adapters.")
            return None

        # This is the core of the new system: using a real merging algorithm
        print(f"Synthesizing {len(all_models_layers)} adapters using TIES...")
        merged_layers = ties_simple_synthesize(all_models_layers, alphas=alphas)

        # Reconstruct the state_dict with generic layer names
        # In a real scenario, you'd need to map these back to the original keys
        # or have a shared architecture definition.
        synthesized_model_dict = {f"layer_{i}": tensor for i, tensor in enumerate(merged_layers)}

        print("Synthesis complete.")
        return synthesized_model_dict

    def save_model(self, model_dict: Dict[str, np.ndarray], output_path: str):
        """Saves a synthesized model to a .safetensors file."""
        try:
            save_file(model_dict, output_path)
            print(f"Synthesized model saved to {output_path}")
        except Exception as e:
            print(f"Error saving model to {output_path}: {e}")

# Example Usage (for testing)
if __name__ == '__main__':
    # This example assumes you have dummy adapter files
    # Let's create some for a quick test
    dummy_tensors_A = {"weight1": np.random.rand(10, 20).astype("float32"), "weight2": np.random.rand(20, 5).astype("float32")}
    dummy_tensors_B = {"weight1": np.random.rand(10, 20).astype("float32"), "weight2": np.random.rand(20, 5).astype("float32")}
    save_file(dummy_tensors_A, "dummy_adapter_A.safetensors")
    save_file(dummy_tensors_B, "dummy_adapter_B.safetensors")

    synthesizer = Synthesizer()
    new_model = synthesizer.synthesize(["dummy_adapter_A.safetensors", "dummy_adapter_B.safetensors"])

    if new_model:
        print("Synthesized model keys:", new_model.keys())
        print("Preview of layer_0:", new_model['layer_0'][:2, :2])
        synthesizer.save_model(new_model, "synthesized_adapter.safetensors")
