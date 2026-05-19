from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentlantern.frameworks.crewai.analyzer import CrewAIProject, _all_tools_in_project


# ── Schema definitions (derived from CrewAI 0.102.0) ─────────────────────────

_AGENT_REQUIRED = {"role", "goal", "backstory"}

_AGENT_FIELDS: dict[str, type | tuple] = {
    "role": str,
    "goal": str,
    "backstory": str,
    "llm": (str, dict),
    "tools": list,
    "function_calling_llm": dict,
    "max_iter": int,
    "max_rpm": int,
    "max_execution_time": (int, float),
    "memory": bool,
    "verbose": bool,
    "allow_delegation": bool,
    "step_callback": dict,
    "cache": bool,
    "system_template": str,
    "prompt_template": str,
    "response_template": str,
    "allow_code_execution": bool,
    "max_retry_limit": int,
    "respect_context_window": bool,
    "code_execution_mode": str,
    "embedder": dict,
    "knowledge_sources": list,
    "use_system_prompt": bool,
}

_TASK_REQUIRED = {"description", "expected_output"}

_TASK_FIELDS: dict[str, type | tuple] = {
    "description": str,
    "expected_output": str,
    "name": str,
    "agent": (str, dict),
    "tools": list,
    "context": list,
    "async_execution": bool,
    "human_input": bool,
    "config": dict,
    "output_file": str,
    "output_json": dict,
    "output_pydantic": dict,
    "callback": dict,
}


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LintFinding:
    severity: str        # "error", "warning", "info"
    code: str            # e.g. "E001"
    message: str
    location: str        # e.g. "agent `researcher`" or "task `analyze`"
    file: str | None = None   # relative path to the source file
    line: int | None = None   # 1-based line number


# ── Entry point ───────────────────────────────────────────────────────────────

def lint_crewai(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    findings.extend(_check_agents(project))
    findings.extend(_check_tasks(project))
    findings.extend(_check_tools(project))
    findings.extend(_check_metadata(project))
    findings.extend(_check_prompts(project))
    findings.extend(_check_yaml_schemas(project))
    return findings


# ── Existing rules ────────────────────────────────────────────────────────────

def _check_agents(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    agent_names = set(project.agents.keys())
    tasks_by_agent: dict[str, list[str]] = {name: [] for name in agent_names}

    for task_name, task_config in project.tasks.items():
        agent = task_config.get("agent")
        if agent:
            tasks_by_agent.setdefault(agent, []).append(task_name)

    for agent_name in agent_names:
        if not tasks_by_agent.get(agent_name):
            findings.append(LintFinding(
                severity="warning",
                code="W001",
                message=f"Agent `{agent_name}` is declared but has no task assigned.",
                location=f"agent `{agent_name}`",
            ))

    for method in project.agent_methods.values():
        if method.allow_delegation is True and len(project.agents) <= 1:
            findings.append(LintFinding(
                severity="warning",
                code="W002",
                message=f"Agent `{method.name}` has `allow_delegation=True` but it is the only agent in the crew.",
                location=f"agent `{method.name}`",
            ))

    return findings


def _check_tasks(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    agent_names = set(project.agents.keys())

    for task_name, task_config in project.tasks.items():
        agent = task_config.get("agent")
        if not agent:
            findings.append(LintFinding(
                severity="error",
                code="E001",
                message=f"Task `{task_name}` has no declared agent.",
                location=f"task `{task_name}`",
            ))
        elif agent not in agent_names:
            findings.append(LintFinding(
                severity="error",
                code="E002",
                message=f"Task `{task_name}` references agent `{agent}` which is not declared in agents.yaml.",
                location=f"task `{task_name}`",
            ))

        expected_output = str(task_config.get("expected_output") or "").strip()
        if not expected_output:
            findings.append(LintFinding(
                severity="warning",
                code="W003",
                message=f"Task `{task_name}` has no expected output declared.",
                location=f"task `{task_name}`",
            ))

    return findings


def _check_tools(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    if not _all_tools_in_project(project):
        findings.append(LintFinding(
            severity="info",
            code="I001",
            message="No tool detected in crew.py — may be intentional for a pure LLM workflow.",
            location="crew",
        ))
    return findings


def _check_metadata(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    pyproject = project.root / "pyproject.toml"
    if not pyproject.exists():
        findings.append(LintFinding(
            severity="warning",
            code="W004",
            message="No `pyproject.toml` found — project metadata is missing.",
            location="project",
        ))
        return findings

    try:
        import tomllib
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        meta = data.get("project", {})
        for author in meta.get("authors", []):
            if not isinstance(author, dict):
                continue
            if author.get("name") == "Your Name" or author.get("email") == "you@example.com":
                findings.append(LintFinding(
                    severity="info",
                    code="I002",
                    message="Project metadata still uses CrewAI template placeholder values in `pyproject.toml`.",
                    location="pyproject.toml",
                ))
                break
    except Exception:
        pass
    return findings


def _check_prompts(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for agent_name, agent_config in project.agents.items():
        role = str(agent_config.get("role") or "").strip()
        goal = str(agent_config.get("goal") or "").strip()
        if len(role) < 5:
            findings.append(LintFinding(
                severity="warning",
                code="W005",
                message=f"Agent `{agent_name}` has a very short role ({len(role)} chars) — may be too vague.",
                location=f"agent `{agent_name}`",
            ))
        if len(goal) > 500:
            findings.append(LintFinding(
                severity="info",
                code="I003",
                message=f"Agent `{agent_name}` goal is very long ({len(goal)} chars) — consider a more concise goal.",
                location=f"agent `{agent_name}`",
            ))

    for task_name, task_config in project.tasks.items():
        desc = str(task_config.get("description") or "").strip()
        if len(desc) > 800:
            findings.append(LintFinding(
                severity="info",
                code="I004",
                message=f"Task `{task_name}` description is very long ({len(desc)} chars) — consider extracting to a template.",
                location=f"task `{task_name}`",
            ))

    return findings


# ── New YAML schema rules ─────────────────────────────────────────────────────

def _check_yaml_schemas(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    findings.extend(_check_agent_yaml(project))
    findings.extend(_check_task_yaml(project))
    return findings


def _check_agent_yaml(project: CrewAIProject) -> list[LintFinding]:
    import yaml as _yaml
    findings: list[LintFinding] = []
    known_lower = {k.lower(): k for k in _AGENT_FIELDS}
    rel_path = str(project.agents_config_path.relative_to(project.root))
    line_map = _yaml_line_map(project.agents_config_path)

    for agent_name, config in project.agents.items():
        loc = f"agents.yaml › `{agent_name}`"
        agent_line = line_map.get(agent_name)

        # W006 — required field missing
        for field in _AGENT_REQUIRED:
            value = str(config.get(field) or "").strip()
            if not value:
                findings.append(LintFinding(
                    severity="warning", code="W006",
                    message=f"Agent `{agent_name}` is missing required field `{field}`.",
                    location=loc, file=rel_path, line=agent_line,
                ))

        for field, value in config.items():
            field_line = line_map.get(f"{agent_name}.{field}", agent_line)
            if field in _AGENT_FIELDS:
                finding = _check_type(field, value, _AGENT_FIELDS[field], loc)
                if finding:
                    findings.append(LintFinding(
                        **{**finding.__dict__, "file": rel_path, "line": field_line}
                    ))
            else:
                suggestion = known_lower.get(field.lower())
                if suggestion:
                    msg = f"Agent `{agent_name}` field `{field}` has incorrect casing — use `{suggestion}` instead."
                else:
                    msg = f"Agent `{agent_name}` has unknown field `{field}` — possible typo."
                findings.append(LintFinding(
                    severity="warning", code="W007",
                    message=msg, location=loc, file=rel_path, line=field_line,
                ))

    return findings


def _check_task_yaml(project: CrewAIProject) -> list[LintFinding]:
    findings: list[LintFinding] = []
    known_lower = {k.lower(): k for k in _TASK_FIELDS}
    rel_path = str(project.tasks_config_path.relative_to(project.root))
    line_map = _yaml_line_map(project.tasks_config_path)

    for task_name, config in project.tasks.items():
        loc = f"tasks.yaml › `{task_name}`"
        task_line = line_map.get(task_name)

        # W006 — description missing
        if not str(config.get("description") or "").strip():
            findings.append(LintFinding(
                severity="warning", code="W006",
                message=f"Task `{task_name}` is missing required field `description`.",
                location=loc, file=rel_path, line=task_line,
            ))

        for field, value in config.items():
            field_line = line_map.get(f"{task_name}.{field}", task_line)
            if field in _TASK_FIELDS:
                finding = _check_type(field, value, _TASK_FIELDS[field], loc)
                if finding:
                    findings.append(LintFinding(
                        **{**finding.__dict__, "file": rel_path, "line": field_line}
                    ))
            else:
                suggestion = known_lower.get(field.lower())
                if suggestion:
                    msg = f"Task `{task_name}` field `{field}` has incorrect casing — use `{suggestion}` instead."
                else:
                    msg = f"Task `{task_name}` has unknown field `{field}` — possible typo."
                findings.append(LintFinding(
                    severity="warning", code="W007",
                    message=msg, location=loc, file=rel_path, line=field_line,
                ))

    return findings


def _yaml_line_map(path) -> dict[str, int]:
    """Return {key: line, "parent.key": line} from a YAML file using compose()."""
    import yaml as _yaml
    from pathlib import Path
    result: dict[str, int] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
        root = _yaml.compose(text)
        if root is None or not hasattr(root, "value"):
            return result
        # root.value is list of (key_node, value_node) pairs
        for key_node, val_node in root.value:
            parent = key_node.value
            result[parent] = key_node.start_mark.line + 1
            if hasattr(val_node, "value") and isinstance(val_node.value, list):
                for child_key, _ in val_node.value:
                    result[f"{parent}.{child_key.value}"] = child_key.start_mark.line + 1
    except Exception:
        pass
    return result


def _check_type(field: str, value: Any, expected: type | tuple, location: str) -> LintFinding | None:
    if value is None:
        return None
    types = expected if isinstance(expected, tuple) else (expected,)

    # bool must be checked before int because isinstance(True, int) is True in Python
    if bool in types:
        if not isinstance(value, bool):
            return LintFinding(
                severity="warning",
                code="W008",
                message=f"`{field}` should be a boolean (`true`/`false`), got `{type(value).__name__}: {value!r}`.",
                location=location,
            )
        return None

    if not isinstance(value, types):
        expected_names = " or ".join(t.__name__ for t in types)
        return LintFinding(
            severity="warning",
            code="W008",
            message=f"`{field}` should be {expected_names}, got `{type(value).__name__}: {value!r}`.",
            location=location,
        )
    return None
