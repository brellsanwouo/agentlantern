from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentlantern.core.base import BaseAnalyzer, BaseProject, StubRenderer, detect_dependency


@dataclass(frozen=True)
class LangGraphProject(BaseProject):
    pass


class LangGraphAnalyzer(BaseAnalyzer):
    framework_name = "LangGraph"

    def detect(self, root: Path) -> bool:
        return detect_dependency(root, "langgraph")

    def analyze(self, root: Path) -> LangGraphProject:
        return LangGraphProject(
            root=root.resolve(),
            name=root.resolve().name,
            framework="LangGraph",
        )

    def get_renderer(self) -> StubRenderer:
        return StubRenderer("LangGraph")
