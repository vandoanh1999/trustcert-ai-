"""
ASA-Fusion v2.0 - Plugin-Based Decision Procedures
Extensible architecture for decision procedures and solvers.

This code is integrated from the Trustcert-ai project.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

from .crypto import ValidationError

class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass

class DecisionResult(Enum):
    """Result of a decision procedure."""
    SAT = "satisfiable"
    UNSAT = "unsatisfiable"
    UNKNOWN = "unknown"
    ERROR = "error"

class DecisionPlugin(ABC):
    """Base class for decision procedure plugins."""
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.enabled = True

    @abstractmethod
    def check(self, data: Any, context: Optional[Dict[str, Any]] = None) -> DecisionResult:
        """
        Run the decision procedure check on the given data.
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {"name": self.name, "version": self.version, "enabled": self.enabled}

class MockSafetyPlugin(DecisionPlugin):
    """
    A mock plugin that checks for sensitive content.
    This simulates a real safety-checker plugin.
    """
    def __init__(self):
        super().__init__("MockSafety", "1.0")
        self.forbidden_keywords = ["password", "secret", "private_key"]

    def check(self, data: Any, context: Optional[Dict[str, Any]] = None) -> DecisionResult:
        if not isinstance(data, str):
            return DecisionResult.ERROR

        if any(keyword in data.lower() for keyword in self.forbidden_keywords):
            print(f"Safety plugin found forbidden keyword in response.")
            return DecisionResult.UNSAT # "Unsatisfiable" in terms of safety policy

        return DecisionResult.SAT # "Satisfiable" / Safe

class PluginRegistry:
    """Registry for managing decision procedure plugins."""
    def __init__(self):
        self._plugins: Dict[str, DecisionPlugin] = {}

    def register(self, plugin: DecisionPlugin):
        if plugin.name in self._plugins:
            raise PluginError(f"Plugin '{plugin.name}' already registered")
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> DecisionPlugin:
        if name not in self._plugins:
            raise PluginError(f"Plugin '{name}' not found")
        return self._plugins[name]

    def list(self) -> List[Dict[str, Any]]:
        return [p.get_info() for p in self._plugins.values()]

    def run_check(self, plugin_name: str, data: Any, context: Optional[Dict[str, Any]] = None) -> DecisionResult:
        plugin = self.get(plugin_name)
        if not plugin.enabled:
            raise PluginError(f"Plugin '{plugin_name}' is disabled")
        return plugin.check(data, context)
