"""
ASA-Fusion v2.0 - Input Validation and Security Hardening
Comprehensive input validation with security checks.

This code is integrated from the Trustcert-ai project.
"""

import re
from typing import Any, Dict, List, Optional, Union

# --- Using exceptions defined in crypto.py for consistency ---
from .crypto import ValidationError

class SecurityError(ValidationError):
    """Exception for security threat detection."""
    pass

class InputValidator:
    """Comprehensive input validator with security hardening for AI prompts."""

    # Security patterns
    SQL_INJECTION_PATTERN = re.compile(
        r"(\bSELECT\b|\bUNION\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
        re.IGNORECASE
    )
    XSS_PATTERN = re.compile(
        r"<script|javascript:|onerror=|onload=",
        re.IGNORECASE
    )
    PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./|\.\.\\")

    def __init__(self, max_prompt_size: int = 4096):
        self.max_prompt_size = max_prompt_size

    def validate_and_sanitize_prompt(self, prompt: str, field_name: str = "prompt") -> str:
        """
        A single, powerful function to validate, check for threats, and sanitize a prompt.

        Returns:
            The sanitized, safe prompt.

        Raises:
            ValidationError: If length or format constraints are violated.
            SecurityError: If a potential threat is detected.
        """
        if not isinstance(prompt, str):
            raise ValidationError(f"{field_name} must be a string.")

        # Length check
        if len(prompt) > self.max_prompt_size:
            raise ValidationError(f"{field_name} exceeds maximum length of {self.max_prompt_size} characters.")

        # Security threat checks
        if self.SQL_INJECTION_PATTERN.search(prompt):
            raise SecurityError(f"Potential SQL injection detected in {field_name}.")
        if self.XSS_PATTERN.search(prompt):
            raise SecurityError(f"Potential XSS attack detected in {field_name}.")
        if self.PATH_TRAVERSAL_PATTERN.search(prompt):
            raise SecurityError(f"Potential path traversal detected in {field_name}.")

        # Sanitization
        sanitized_prompt = prompt.replace('\x00', '') # Remove null bytes
        sanitized_prompt = ''.join(char for char in sanitized_prompt if char.isprintable() or char in '\n\t')

        return sanitized_prompt.strip()

# Example Usage
if __name__ == '__main__':
    validator = InputValidator()

    safe_prompt = "Hello, world. Please write a function in Python."
    sanitized = validator.validate_and_sanitize_prompt(safe_prompt)
    print(f"Safe prompt is clean: {sanitized == safe_prompt.strip()}")

    xss_prompt = "<script>alert('XSS')</script>"
    try:
        validator.validate_and_sanitize_prompt(xss_prompt)
    except SecurityError as e:
        print(f"Successfully caught XSS attack: {e}")

    long_prompt = "a" * 5000
    try:
        validator.validate_and_sanitize_prompt(long_prompt)
    except ValidationError as e:
        print(f"Successfully caught long prompt: {e}")
