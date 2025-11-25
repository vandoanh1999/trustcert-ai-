"""
Genesis Core V5: The Arbiter Module

This module integrates the core concepts from the Trustcert-ai project,
providing a powerful verification and certification layer for AI responses.
"""

from .crypto import SHA3CertificateManager, Certificate
from .validation import InputValidator, SecurityError
from .plugins import PluginRegistry, MockSafetyPlugin, DecisionResult

class Arbiter:
    """
    A unified interface for validation, safety checks, and certification.
    This class acts as the central point of contact for the V5 pipeline.
    """
    def __init__(self):
        self.validator = InputValidator()
        self.cert_manager = SHA3CertificateManager()

        # Initialize and register default plugins
        self.plugin_registry = PluginRegistry()
        self.plugin_registry.register(MockSafetyPlugin())
        print("Arbiter initialized with default 'MockSafety' plugin.")

    def inspect_and_certify(self, prompt: str, response: str, metadata: dict) -> (dict, dict):
        """
        Performs a full inspection and certification pipeline.

        Returns:
            A tuple of (verification_report, certificate_dict)
        """
        # 1. Validate the incoming prompt for safety
        try:
            self.validator.validate_and_sanitize_prompt(prompt)
        except (ValidationError, SecurityError) as e:
            report = {"status": "REJECTED", "reason": f"Invalid prompt: {e}"}
            return report, None

        # 2. Run safety checks on the AI's response using plugins
        verification_status = "PASSED"
        plugin_results = {}
        for plugin_info in self.plugin_registry.list():
            plugin_name = plugin_info['name']
            result = self.plugin_registry.run_check(plugin_name, response)
            plugin_results[plugin_name] = result.value
            if result != DecisionResult.SAT:
                verification_status = "FAILED_SAFETY_CHECK"

        report = {
            "status": verification_status,
            "plugins": plugin_results
        }

        # 3. If all checks pass, create a certificate
        if verification_status == "PASSED":
            # We certify a combination of prompt and response to ensure context
            cert_data = f"PROMPT: {prompt}\nRESPONSE: {response}"
            certificate = self.cert_manager.create_certificate(cert_data, metadata=metadata)
            return report, certificate.to_dict()

        return report, None

__all__ = ["Arbiter", "Certificate", "SecurityError", "DecisionResult"]
