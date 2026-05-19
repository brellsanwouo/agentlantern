from __future__ import annotations

from pathlib import Path

from agentlantern.core.base import BaseAnalyzer, NoFrameworkDetected
from agentlantern.frameworks.autogen.analyzer import AutoGenAnalyzer
from agentlantern.frameworks.crewai.analyzer import CrewAIAnalyzer
from agentlantern.frameworks.google_adk.analyzer import GoogleADKAnalyzer
from agentlantern.frameworks.langgraph.analyzer import LangGraphAnalyzer
from agentlantern.frameworks.smolagents.analyzer import SmolagentsAnalyzer

REGISTRY: list[BaseAnalyzer] = [
    CrewAIAnalyzer(),
    LangGraphAnalyzer(),
    AutoGenAnalyzer(),
    SmolagentsAnalyzer(),
    GoogleADKAnalyzer(),
]

SUPPORTED_FRAMEWORKS = [a.framework_name for a in REGISTRY]


def detect_framework(root: Path) -> BaseAnalyzer:
    """Return the first analyzer that recognizes the project, or raise NoFrameworkDetected."""
    for analyzer in REGISTRY:
        if analyzer.detect(root):
            return analyzer
    raise NoFrameworkDetected(
        f"No supported multi-agent framework detected in {root}.\n"
        f"Supported frameworks: {', '.join(SUPPORTED_FRAMEWORKS)}."
    )
