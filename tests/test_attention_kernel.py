"""
Unit Tests for the Compliant Attention Kernel.

This test suite verifies the correctness, robustness, and adherence to
quality gates for the `execute_attention_kernel` and its helper functions.
"""
import unittest
import torch
from genesis_core.inference.kernel.attention_kernel import execute_attention_kernel

class TestAttentionKernel(unittest.TestCase):

    def setUp(self):
        """Set up common tensors for testing."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Running tests on device: {self.device}")

        self.batch_size = 2
        self.num_heads = 4
        self.seq_len = 16
        self.d_head = 32

        # Create valid complex-valued tensors
        self.q = torch.randn(self.batch_size, self.num_heads, self.seq_len, self.d_head, dtype=torch.complex64, device=self.device)
        self.k = torch.randn(self.batch_size, self.num_heads, self.seq_len, self.d_head, dtype=torch.complex64, device=self.device)
        self.v = torch.randn(self.batch_size, self.num_heads, self.seq_len, self.d_head, dtype=torch.complex64, device=self.device)

    def test_successful_execution(self):
        """
        Test the kernel runs without errors with valid inputs.
        (Testability Gate: Happy Path)
        """
        try:
            output, fused_idx, worst_idx = execute_attention_kernel(self.q, self.k, self.v)
            self.assertIsNotNone(output)
            self.assertIsNotNone(fused_idx)
            self.assertIsNotNone(worst_idx)
        except Exception as e:
            self.fail(f"Kernel execution failed with valid inputs: {e}")

    def test_output_shape_and_type(self):
        """
        Verify the output tensors have the correct shape and dtype.
        (Verification Phase: Shape and Type Assurance)
        """
        output, _, _ = execute_attention_kernel(self.q, self.k, self.v)

        self.assertEqual(output.shape, self.q.shape)
        self.assertTrue(torch.is_complex(output))
        self.assertEqual(output.device.type, self.device)

    def test_validation_gate_mismatched_devices(self):
        """
        Test that the validation gate catches tensors on different devices.
        (Testability Gate: Error Flow Isolation)
        """
        if torch.cuda.is_available() and torch.cuda.device_count() > 0:
            # This test can only run if a CUDA device is present.
            k_cpu = self.k.to("cpu")
            with self.assertRaisesRegex(ValueError, "All tensors must be on the same device"):
                execute_attention_kernel(self.q, k_cpu, self.v)
        else:
            self.skipTest("CUDA device not available for mismatched device test.")

    def test_validation_gate_incorrect_dtype(self):
        """
        Test that the validation gate catches non-complex tensors.
        (Verification Phase: Data Type Checks)
        """
        q_float = self.q.real
        with self.assertRaisesRegex(ValueError, "All input tensors must be of complex dtype"):
            execute_attention_kernel(q_float, self.k, self.v)

    def test_validation_gate_invalid_dimensions(self):
        """
        Test that the validation gate catches tensors with incorrect dimensions.
        """
        # Create a 3D tensor by slicing, which is guaranteed to work.
        q_3d = self.q[0]
        with self.assertRaisesRegex(ValueError, "Inputs must be 4D tensors"):
            execute_attention_kernel(q_3d, self.k, self.v)

    def test_index_handling(self):
        """
        Verify that `fused_idx` and `worst_idx` have the correct shapes.
        (Verification Phase: Proper Handling of Indices)
        """
        _, fused_idx, worst_idx = execute_attention_kernel(self.q, self.k, self.v)

        # Fused_idx should have shape (seq_len, 2) because we ask for top 2
        self.assertEqual(fused_idx.shape, (self.seq_len, 2))

        # Worst_idx should have shape (seq_len,) as it's the argmin over the last dim
        self.assertEqual(worst_idx.shape, (self.seq_len,))

    def test_determinism(self):
        """
        Ensure the kernel produces reproducible results given the same input.
        (Verification Phase: Defined and Reproducible Behavior)
        """
        # Manual seed for reproducibility
        torch.manual_seed(42)
        q1 = torch.randn_like(self.q)
        k1 = torch.randn_like(self.k)
        v1 = torch.randn_like(self.v)

        output1, _, _ = execute_attention_kernel(q1, k1, v1)

        torch.manual_seed(42)
        q2 = torch.randn_like(self.q)
        k2 = torch.randn_like(self.k)
        v2 = torch.randn_like(self.v)

        output2, _, _ = execute_attention_kernel(q2, k2, v2)

        # Check if the outputs are close enough.
        # Use a tolerance for floating-point comparisons.
        self.assertTrue(torch.allclose(output1.real, output2.real, atol=1e-6))
        self.assertTrue(torch.allclose(output1.imag, output2.imag, atol=1e-6))


if __name__ == '__main__':
    unittest.main()
