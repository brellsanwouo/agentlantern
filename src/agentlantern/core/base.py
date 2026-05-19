from __future__ import annotations

import tomllib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BaseProject:
    root: Path
    name: str
    framework: str


class NoFrameworkDetected(Exception):
    pass


class BaseAnalyzer(ABC):
    framework_name: str

    @abstractmethod
    def detect(self, root: Path) -> bool: ...

    @abstractmethod
    def analyze(self, root: Path) -> BaseProject: ...

    @abstractmethod
    def get_renderer(self) -> "BaseRenderer": ...


_SIDEBAR_LABELS: dict[str, str] = {
    "overview.md": "Overview",
    "architecture.md": "Architecture",
    "agents.md": "Agents",
    "tasks.md": "Tasks",
    "tools.md": "Tools",
    "workflows.md": "Workflows",
    "diagrams.md": "Diagrams",
    "runbook.md": "Runbook",
    "contact.md": "**Contact**",
}


class BaseRenderer(ABC):
    @abstractmethod
    def render_overview(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_architecture(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_agents(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_tasks(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_diagrams(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_runbook(self, project: BaseProject) -> str: ...

    @abstractmethod
    def render_contact(self, project: BaseProject) -> str: ...

    def get_doc_structure(self, project: BaseProject) -> list[tuple[str, str]]:
        """Return ordered (filename, content) pairs for this framework.

        Override in framework renderers to add, remove, or rename sections.
        """
        return [
            ("overview.md",      self.render_overview(project)),
            ("architecture.md",  self.render_architecture(project)),
            ("diagrams.md",      self.render_diagrams(project)),
            ("agents.md",        self.render_agents(project)),
            ("tasks.md",         self.render_tasks(project)),
            ("runbook.md",       self.render_runbook(project)),
            ("contact.md",       self.render_contact(project)),
        ]

    def render_sidebar(self, structure: list[tuple[str, str]]) -> str:
        """Generate Docsify _sidebar.md from the doc structure."""
        lines = ["- **[AgentLantern](https://github.com/brellsanwouo/agentlantern)**"]
        for filename, _ in structure:
            label = _SIDEBAR_LABELS.get(filename, filename.removesuffix(".md").title())
            lines.append(f"  - [{label}]({filename})")
        lines.append("")
        return "\n".join(lines)


class StubRenderer(BaseRenderer):
    """Renderer for frameworks detected but not yet fully analyzed."""

    def __init__(self, framework_name: str) -> None:
        self._name = framework_name

    def _stub(self, section: str, project: BaseProject) -> str:
        from agentlantern.core.pyproject import read_metadata, read_contacts
        metadata = read_metadata(project.root)
        contacts = read_contacts(project.root)
        contact_str = (
            ", ".join(f"{c['name']} <{c['email']}>" for c in contacts)
            if contacts else "not declared"
        )
        return "\n".join([
            f"# {section}",
            "",
            f"> **{self._name} support — full analysis coming soon.**",
            "",
            f"[AgentLantern](https://github.com/brellsanwouo/agentlantern) detected a **{self._name}** project "
            f"(`{project.name}`) but detailed analysis for this framework is not yet implemented.",
            "",
            "## Project Information",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Name | `{project.name}` |",
            f"| Framework | `{self._name}` |",
            f"| Version | `{metadata.get('version', 'not declared')}` |",
            f"| Python | `{metadata.get('requires-python', 'not declared')}` |",
            f"| Contact | `{contact_str}` |",
            "",
        ])

    def render_overview(self, project: BaseProject) -> str:
        return self._stub("Overview", project)

    def render_architecture(self, project: BaseProject) -> str:
        return self._stub("Architecture", project)

    def render_agents(self, project: BaseProject) -> str:
        return self._stub("Agents", project)

    def render_tasks(self, project: BaseProject) -> str:
        return self._stub("Tasks", project)

    def render_diagrams(self, project: BaseProject) -> str:
        return self._stub("Diagrams", project)

    def render_runbook(self, project: BaseProject) -> str:
        return self._stub("Runbook", project)

    def render_contact(self, project: BaseProject) -> str:
        from agentlantern.core.pyproject import read_contacts
        contacts = read_contacts(project.root)
        lines = [
            "# Contact",
            "",
            "Contact information extracted from `pyproject.toml`.",
            "",
            "| Name | Email | Source |",
            "| --- | --- | --- |",
        ]
        if not contacts:
            lines.append("| `not declared` | `not declared` | `pyproject.toml` |")
        else:
            for c in contacts:
                lines.append(f"| `{c['name']}` | `{c['email']}` | `pyproject.toml` |")
        lines.append("")
        return "\n".join(lines)


def detect_dependency(root: Path, *package_names: str) -> bool:
    """Return True if any package_name appears in pyproject.toml dependencies."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        deps = data.get("project", {}).get("dependencies", [])
        for dep in deps:
            for name in package_names:
                if name.lower() in dep.lower():
                    return True
    except Exception:
        pass
    return False
