from __future__ import annotations

import json
from pathlib import Path

from agentlantern.frameworks.registry import detect_framework


def run_inspect(project_root: Path) -> None:
    root = project_root.resolve()
    analyzer = detect_framework(root)
    project = analyzer.analyze(root)
    payload = _serialize(project)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _serialize(project) -> dict:
    framework = project.framework

    if framework == "CrewAI":
        return _serialize_crewai(project)

    return {
        "name": project.name,
        "framework": framework,
        "root": str(project.root),
    }


def _serialize_crewai(project) -> dict:
    agents = []
    for agent_name, config in project.agents.items():
        method = next(
            (m for m in project.agent_methods.values()
             if m.config_key == agent_name or m.name == agent_name),
            None,
        )
        tasks = [
            t for t, tc in project.tasks.items()
            if tc.get("agent") == agent_name
        ]
        agents.append({
            "name": agent_name,
            "role": config.get("role"),
            "goal": config.get("goal"),
            "tools": method.tools if method else [],
            "llm": method.llm if method else None,
            "allow_delegation": method.allow_delegation if method else None,
            "memory": method.memory if method else None,
            "tasks": tasks,
            "file": str(project.crew_path.relative_to(project.root)) if project.crew_path else None,
            "line": method.line if method and hasattr(method, "line") else None,
        })

    tasks = []
    for task_name, config in project.tasks.items():
        method = next(
            (m for m in project.task_methods.values()
             if m.config_key == task_name or m.name == task_name),
            None,
        )
        tasks.append({
            "name": task_name,
            "agent": config.get("agent"),
            "description": config.get("description"),
            "expected_output": config.get("expected_output"),
            "output_file": method.output_file if method else None,
            "context": method.context_methods if method else [],
            "file": str(project.crew_path.relative_to(project.root)) if project.crew_path else None,
            "line": method.line if method and hasattr(method, "line") else None,
        })

    return {
        "name": project.name,
        "framework": project.framework,
        "root": str(project.root),
        "crew_file": str(project.crew_path.relative_to(project.root)) if project.crew_path else None,
        "process": project.process,
        "agents": agents,
        "tasks": tasks,
    }
