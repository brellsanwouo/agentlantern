from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentlantern.core.base import BaseAnalyzer, BaseProject, StubRenderer, detect_dependency


@dataclass(frozen=True)
class AutoGenProject(BaseProject):
    pass


class AutoGenAnalyzer(BaseAnalyzer):
    framework_name = "AutoGen"

    def detect(self, root: Path) -> bool:
        return detect_dependency(root, "autogen-agentchat", "pyautogen", "autogen")

    def analyze(self, root: Path) -> AutoGenProject:
        return AutoGenProject(
            root=root.resolve(),
            name=root.resolve().name,
            framework="AutoGen",
        )

    def get_renderer(self) -> StubRenderer:
        return StubRenderer("AutoGen")
