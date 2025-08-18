"""
ReadyTensor - Lightweight Repository Assessment Tool
A streamlined version of rt-repo-assessment with direct OpenAI integration.
"""

__version__ = "1.0.0"
__author__ = "ReadyTensor Team"

from .core.analyzer import RepositoryAnalyzer
from .llm.client import LLMClient
from .config.config_manager import ConfigManager

__all__ = ["RepositoryAnalyzer", "LLMClient", "ConfigManager"]
