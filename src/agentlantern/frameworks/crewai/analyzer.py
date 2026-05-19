from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agentlantern.core.base import BaseAnalyzer, BaseProject, detect_dependency


@dataclass(frozen=True)
class CrewAIProject(BaseProject):
    package_dir: Path
    agents_config_path: Path
    tasks_config_path: Path
    crew_path: Path
    crew_class: str | None
    agents: dict[str, dict[str, Any]]
    tasks: dict[str, dict[str, Any]]
    agent_methods: dict[str, "AgentMethod"]
    task_methods: dict[str, "TaskMethod"]
    crew_methods: dict[str, "CrewMethod"]
    kickoff_calls: list["KickoffCall"]
    process: str | None


@dataclass(frozen=True)
class AgentMethod:
    name: str
    config_key: str | None
    tools: list[str]
    llm: str | None
    allow_delegation: bool | None
    memory: bool | None
    line: int | None = None   # line number of the method in crew.py


@dataclass(frozen=True)
class TaskMethod:
    name: str
    config_key: str | None
    agent_method: str | None
    output_file: str | None
    context_methods: list[str]
    line: int | None = None   # line number of the method in crew.py


@dataclass(frozen=True)
class CrewMethod:
    name: str
    process: str | None


@dataclass(frozen=True)
class KickoffCall:
    file: Path
    function: str | None
    line: int


class CrewAIAnalyzer(BaseAnalyzer):
    framework_name = "CrewAI"

    def detect(self, root: Path) -> bool:
        if detect_dependency(root, "crewai"):
            return True
        try:
            _find_crew_file(root)
            return True
        except FileNotFoundError:
            return False

    def analyze(self, root: Path) -> CrewAIProject:
        return load_crewai_project(root)

    def get_renderer(self):
        from agentlantern.frameworks.crewai.renderer import CrewAIRenderer
        return CrewAIRenderer()


def load_crewai_project(project_root: Path) -> CrewAIProject:
    root = project_root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")

    crew_path = _find_crew_file(root)
    package_dir = crew_path.parent
    crew_class = _parse_crew_class(crew_path)
    agents_config_path = _resolve_config_path(
        root, package_dir, crew_class.agents_config,
        fallback_filename="agents.yaml", yaml_kind="agents",
    )
    tasks_config_path = _resolve_config_path(
        root, package_dir, crew_class.tasks_config,
        fallback_filename="tasks.yaml", yaml_kind="tasks",
    )

    agents = _load_yaml_mapping(agents_config_path)
    tasks = _load_yaml_mapping(tasks_config_path)
    parsed = _parse_crew_file(crew_path)
    kickoff_calls = _find_kickoff_calls(root)

    return CrewAIProject(
        root=root,
        name=root.name,
        framework="CrewAI",
        package_dir=package_dir,
        agents_config_path=agents_config_path,
        tasks_config_path=tasks_config_path,
        crew_path=crew_path,
        crew_class=crew_class.name,
        agents=agents,
        tasks=tasks,
        agent_methods=parsed["agents"],
        task_methods=parsed["tasks"],
        crew_methods=parsed["crews"],
        kickoff_calls=kickoff_calls,
        process=parsed["process"],
    )


def _find_unique(root: Path, filename: str) -> Path:
    matches = [
        path
        for path in root.rglob(filename)
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]
    if not matches:
        raise FileNotFoundError(f"Could not find {filename} under {root}")
    return sorted(matches, key=lambda path: len(path.parts))[0]


@dataclass(frozen=True)
class _CrewClass:
    name: str | None
    agents_config: str | None
    tasks_config: str | None


def _parse_crew_class(path: Path) -> _CrewClass:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        decorator_names = {_decorator_name(decorator) for decorator in node.decorator_list}
        if "CrewBase" not in decorator_names:
            continue
        attrs = _class_string_assignments(node)
        return _CrewClass(
            name=node.name,
            agents_config=attrs.get("agents_config"),
            tasks_config=attrs.get("tasks_config"),
        )
    return _CrewClass(name=None, agents_config=None, tasks_config=None)


def _class_string_assignments(node: ast.ClassDef) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for statement in node.body:
        if not isinstance(statement, ast.Assign):
            continue
        value = _constant_string(statement.value)
        if value is None:
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name):
                assignments[target.id] = value
    return assignments


def _resolve_config_path(
    root: Path, package_dir: Path, configured_path: str | None,
    *, fallback_filename: str, yaml_kind: str,
) -> Path:
    if configured_path:
        for candidate in [package_dir / configured_path, root / configured_path]:
            if candidate.exists():
                return candidate.resolve()
    try:
        return _find_unique(root, fallback_filename)
    except FileNotFoundError:
        inferred = _find_yaml_by_shape(root, yaml_kind)
        if inferred:
            return inferred
        raise


def _find_yaml_by_shape(root: Path, yaml_kind: str) -> Path | None:
    required_keys = {"role", "goal"} if yaml_kind == "agents" else {"description", "expected_output"}
    matches = []
    for path in root.rglob("*.y*ml"):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            data = _load_yaml_mapping(path)
        except Exception:
            continue
        if not data:
            continue
        values = [v for v in data.values() if isinstance(v, dict)]
        if values and all(required_keys <= set(v.keys()) for v in values):
            matches.append(path.resolve())
    return sorted(matches, key=lambda p: len(p.parts))[0] if matches else None


def _find_crew_file(root: Path) -> Path:
    candidates = [
        path
        for path in root.rglob("crew.py")
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]
    if not candidates:
        raise FileNotFoundError(f"Could not find crew.py under {root}")
    return sorted(candidates, key=lambda path: len(path.parts))[0]


def _load_yaml_mapping(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return data


def _parse_crew_file(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    agent_methods: dict[str, AgentMethod] = {}
    task_methods: dict[str, TaskMethod] = {}
    crew_methods: dict[str, CrewMethod] = {}
    process: str | None = None

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        decorator_names = {_decorator_name(d) for d in node.decorator_list}
        if "agent" in decorator_names:
            agent_methods[node.name] = _parse_agent_method(node)
        elif "task" in decorator_names:
            task_methods[node.name] = _parse_task_method(node)
        elif "crew" in decorator_names:
            method_process = _parse_process(node)
            crew_methods[node.name] = CrewMethod(name=node.name, process=method_process)
            process = method_process

    return {"agents": agent_methods, "tasks": task_methods, "crews": crew_methods, "process": process}


def _find_kickoff_calls(root: Path) -> list[KickoffCall]:
    calls: list[KickoffCall] = []
    for path in root.rglob("*.py"):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _call_name(node) == "kickoff":
                function = _enclosing_function(node, parents)
                calls.append(KickoffCall(file=path, function=function, line=node.lineno))
    return calls


def _enclosing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, ast.FunctionDef):
            return current.name
        current = parents.get(current)
    return None


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _parse_agent_method(node: ast.FunctionDef) -> AgentMethod:
    config_key = None
    tools: list[str] = []
    llm: str | None = None
    allow_delegation: bool | None = None
    memory: bool | None = None
    call = _first_returned_call(node, "Agent")
    if call:
        for keyword in call.keywords:
            if keyword.arg == "config":
                config_key = _config_key(keyword.value)
            elif keyword.arg == "tools":
                tools = _list_call_names(keyword.value)
            elif keyword.arg == "llm":
                llm = _name_or_string(keyword.value)
            elif keyword.arg == "allow_delegation":
                allow_delegation = _bool_constant(keyword.value)
            elif keyword.arg == "memory":
                memory = _bool_constant(keyword.value)
    return AgentMethod(
        name=node.name,
        config_key=config_key,
        tools=tools,
        llm=llm,
        allow_delegation=allow_delegation,
        memory=memory,
        line=node.lineno,
    )


def _parse_task_method(node: ast.FunctionDef) -> TaskMethod:
    config_key = None
    agent_method = None
    output_file = None
    context_methods: list[str] = []
    call = _first_returned_call(node, "Task")
    if call:
        for keyword in call.keywords:
            if keyword.arg == "config":
                config_key = _config_key(keyword.value)
            elif keyword.arg == "agent":
                agent_method = _method_call_name(keyword.value)
            elif keyword.arg == "output_file":
                output_file = _constant_string(keyword.value)
            elif keyword.arg == "context":
                context_methods = _list_method_names(keyword.value)
    return TaskMethod(
        name=node.name,
        config_key=config_key,
        agent_method=agent_method,
        output_file=output_file,
        context_methods=context_methods,
        line=node.lineno,
    )


def _parse_process(node: ast.FunctionDef) -> str | None:
    call = _first_returned_call(node, "Crew")
    if not call:
        return None
    for keyword in call.keywords:
        if keyword.arg == "process":
            value = keyword.value
            if isinstance(value, ast.Attribute):
                return value.attr
            return ast.unparse(value)
    return None


def _first_returned_call(node: ast.FunctionDef, call_name: str) -> ast.Call | None:
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and isinstance(child.value, ast.Call):
            if _call_name(child.value) == call_name:
                return child.value
    return None


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _config_key(node: ast.expr) -> str | None:
    if not isinstance(node, ast.Subscript):
        return None
    return _constant_string(node.slice)


def _constant_string(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _list_call_names(node: ast.expr) -> list[str]:
    if not isinstance(node, ast.List):
        return []
    names = []
    for item in node.elts:
        if isinstance(item, ast.Call):
            names.append(_call_name(item))
        elif isinstance(item, ast.Name):
            names.append(item.id)
    return names


def _method_call_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _name_or_string(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _bool_constant(node: ast.expr) -> bool | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _all_tools_in_project(project: CrewAIProject) -> set[str]:
    tools: set[str] = set()
    for method in project.agent_methods.values():
        tools.update(method.tools)
    return tools


def _list_method_names(node: ast.expr) -> list[str]:
    """Extract method names from context=[self.task1(), self.task2()]."""
    if not isinstance(node, ast.List):
        return []
    names = []
    for item in node.elts:
        name = _method_call_name(item)
        if name:
            names.append(name)
    return names
