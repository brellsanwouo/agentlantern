from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentlantern.core.base import BaseAnalyzer, BaseProject, StubRenderer, detect_dependency


@dataclass(frozen=True)
class SmolagentsProject(BaseProject):
    pass


class SmolagentsAnalyzer(BaseAnalyzer):
    framework_name = "Smolagents"

    def detect(self, root: Path) -> bool:
        return detect_dependency(root, "smolagents")

    def analyze(self, root: Path) -> SmolagentsProject:
        return SmolagentsProject(
            root=root.resolve(),
            name=root.resolve().name,
            framework="Smolagents",
        )

    def get_renderer(self) -> StubRenderer:
        return StubRenderer("Smolagents")
