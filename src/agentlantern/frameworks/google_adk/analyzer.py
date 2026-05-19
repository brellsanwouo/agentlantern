from __future__ import annotations

import ast
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentlantern.core.base import BaseAnalyzer, BaseProject, detect_dependency


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ADKAgentInfo:
    class_name: str
    adk_name: str | None        # from super().__init__(name=...)
    description: str | None
    file: Path
    line: int
    base_classes: list[str]
    tools: list[str]            # tool function / class names referenced
    sub_agents: list[str]       # other agent class names referenced


@dataclass(frozen=True)
class ADKToolInfo:
    name: str
    description: str | None     # first line of docstring
    parameters: list[str]
    file: Path
    line: int
    is_adk_decorated: bool      # @tool or @FunctionTool decorator


@dataclass(frozen=True)
class ADKEntryPoint:
    command: str                # CLI command name e.g. "aware"
    target: str                 # e.g. "cli.main:run"


@dataclass(frozen=True)
class ADKCliCommand:
    name: str
    description: str | None
    file: Path


@dataclass(frozen=True)
class GoogleADKProject(BaseProject):
    agents: list[ADKAgentInfo]
    tools: list[ADKToolInfo]
    entry_points: list[ADKEntryPoint]
    cli_commands: list[ADKCliCommand]
    env_vars: dict[str, set[str]]
    pydantic_models: list[str]
    llm_providers: list[str]
    package_metadata: dict[str, Any]


# ── Analyzer ──────────────────────────────────────────────────────────────────

# Known Google ADK base class names
_ADK_BASE_CLASSES = {
    "BaseAgent", "LlmAgent", "Agent", "SequentialAgent",
    "ParallelAgent", "LoopAgent", "MultiAgent",
}

_ADK_TOOL_DECORATORS = {"tool", "FunctionTool", "adk_tool"}


class GoogleADKAnalyzer(BaseAnalyzer):
    framework_name = "Google ADK"

    def detect(self, root: Path) -> bool:
        return detect_dependency(root, "google-adk", "google-cloud-aiplatform")

    def analyze(self, root: Path) -> GoogleADKProject:
        return load_google_adk_project(root)

    def get_renderer(self):
        from agentlantern.frameworks.google_adk.renderer import GoogleADKRenderer
        return GoogleADKRenderer()


# ── Project loader ─────────────────────────────────────────────────────────────

def load_google_adk_project(project_root: Path) -> GoogleADKProject:
    root = project_root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Project path does not exist: {root}")

    py_files = _collect_python_files(root)

    # Pass 1: collect all class definitions and inheritance
    class_registry: dict[str, str] = {}  # class_name -> file path string
    inheritance: dict[str, list[str]] = {}  # class_name -> list of base names
    for path in py_files:
        _collect_classes(path, class_registry, inheritance)

    # Pass 2: resolve ADK agent classes (direct + indirect inheritance)
    adk_classes = _resolve_adk_classes(inheritance)

    # Pass 3: extract agent details (topologically sorted: root first, leaves last)
    agents = _topological_sort_agents(_extract_agents(py_files, adk_classes, inheritance))

    # Pass 4: collect tools
    tools = _extract_tools(py_files, root)

    # Pass 5: entry points and CLI commands
    metadata = _read_pyproject(root)
    entry_points = _extract_entry_points(metadata)
    cli_commands = _extract_cli_commands(py_files)

    # Pass 6: environment variables
    env_vars = _extract_env_vars(root, py_files)

    # Pass 7: Pydantic models
    pydantic_models = _extract_pydantic_models(py_files)

    # Pass 8: LLM providers
    llm_providers = _extract_llm_providers(py_files, root)

    return GoogleADKProject(
        root=root,
        name=metadata.get("name", root.name),
        framework="Google ADK",
        agents=agents,
        tools=tools,
        entry_points=entry_points,
        cli_commands=cli_commands,
        env_vars=env_vars,
        pydantic_models=pydantic_models,
        llm_providers=llm_providers,
        package_metadata=metadata,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _collect_python_files(root: Path) -> list[Path]:
    return [
        path for path in root.rglob("*.py")
        if ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and ".git" not in path.parts
    ]


def _collect_classes(
    path: Path,
    class_registry: dict[str, str],
    inheritance: dict[str, list[str]],
) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_registry[node.name] = str(path)
            bases = [_base_name(b) for b in node.bases if _base_name(b)]
            inheritance[node.name] = bases


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _resolve_adk_classes(inheritance: dict[str, list[str]]) -> set[str]:
    """Return all class names that inherit (directly or transitively) from ADK base classes."""
    adk = set(_ADK_BASE_CLASSES)
    changed = True
    while changed:
        changed = False
        for cls, bases in inheritance.items():
            if cls not in adk and any(b in adk for b in bases):
                adk.add(cls)
                changed = True
    return adk


def _extract_agents(
    py_files: list[Path],
    adk_classes: set[str],
    inheritance: dict[str, list[str]],
) -> list[ADKAgentInfo]:
    agents: list[ADKAgentInfo] = []
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [_base_name(b) for b in node.bases]
            if not any(b in adk_classes for b in bases):
                continue
            # Skip abstract / generic base classes (they ARE the ADK bases)
            if node.name in _ADK_BASE_CLASSES:
                continue

            adk_name, description = _extract_agent_init_args(node)
            tools = _extract_tool_refs(node, path)
            sub_agents = _extract_sub_agent_refs(node, adk_classes)

            agents.append(ADKAgentInfo(
                class_name=node.name,
                adk_name=adk_name,
                description=description,
                file=path,
                line=node.lineno,
                base_classes=bases,
                tools=tools,
                sub_agents=sub_agents,
            ))
    return agents


def _extract_agent_init_args(cls_node: ast.ClassDef) -> tuple[str | None, str | None]:
    """Extract name= and description= from super().__init__() in __init__."""
    for node in ast.walk(cls_node):
        if not isinstance(node, ast.FunctionDef) or node.name != "__init__":
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            # Match super().__init__(...) or Agent.__init__(self, ...)
            func = child.func
            is_super_init = (
                isinstance(func, ast.Attribute)
                and func.attr == "__init__"
            )
            if not is_super_init:
                continue
            name_val = _kwarg_string(child, "name")
            desc_val = _kwarg_string(child, "description")
            if name_val or desc_val:
                return name_val, desc_val
    return None, None


def _kwarg_string(call: ast.Call, key: str) -> str | None:
    for kw in call.keywords:
        if kw.arg == key and isinstance(kw.value, ast.Constant):
            return str(kw.value.value)
    return None


def _extract_tool_refs(cls_node: ast.ClassDef, file: Path) -> list[str]:
    """Collect names of functions/classes referenced as tools inside the class."""
    tools: list[str] = []
    for node in ast.walk(cls_node):
        if isinstance(node, ast.Call):
            # FunctionTool(my_func) or tool(my_func)
            fname = _call_func_name(node)
            if fname in _ADK_TOOL_DECORATORS:
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        tools.append(arg.id)
            # list of tool names in keyword tools=[...]
            for kw in node.keywords:
                if kw.arg == "tools" and isinstance(kw.value, ast.List):
                    for elt in kw.value.elts:
                        name = _resolve_name_or_call(elt)
                        if name:
                            tools.append(name)
    return list(dict.fromkeys(tools))  # deduplicate preserving order


def _extract_sub_agent_refs(cls_node: ast.ClassDef, adk_classes: set[str]) -> list[str]:
    """Find other ADK agent class names instantiated inside this class."""
    sub: list[str] = []
    for node in ast.walk(cls_node):
        if isinstance(node, ast.Call):
            name = _call_func_name(node)
            if name and name in adk_classes and name != cls_node.name:
                sub.append(name)
    return list(dict.fromkeys(sub))


def _call_func_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _resolve_name_or_call(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return _call_func_name(node)
    return None


def _topological_sort_agents(agents: list[ADKAgentInfo]) -> list[ADKAgentInfo]:
    """BFS from root agents (not referenced as sub-agents) down to leaves."""
    by_class: dict[str, ADKAgentInfo] = {a.class_name: a for a in agents}
    referenced: set[str] = {sub for a in agents for sub in a.sub_agents}
    roots = [a for a in agents if a.class_name not in referenced]

    ordered: list[ADKAgentInfo] = []
    visited: set[str] = set()
    queue = list(roots)
    while queue:
        agent = queue.pop(0)
        if agent.class_name in visited:
            continue
        visited.add(agent.class_name)
        ordered.append(agent)
        for sub_class in agent.sub_agents:
            if sub_class in by_class and sub_class not in visited:
                queue.append(by_class[sub_class])

    for agent in agents:
        if agent.class_name not in visited:
            ordered.append(agent)
    return ordered


def _extract_tools(py_files: list[Path], root: Path) -> list[ADKToolInfo]:
    """Extract tool functions: decorated with @tool or living in tools/ directories."""
    tools: list[ADKToolInfo] = []
    for path in py_files:
        # Prioritise files in directories named "tools"
        in_tools_dir = any(part == "tools" for part in path.relative_to(root).parts)
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            decorator_names = {_base_name(d) for d in node.decorator_list}
            is_decorated = bool(decorator_names & _ADK_TOOL_DECORATORS)
            if not is_decorated and not in_tools_dir:
                continue
            # Skip private functions in tools dir unless decorated
            if not is_decorated and node.name.startswith("_"):
                continue

            docstring = ast.get_docstring(node)
            description = docstring.splitlines()[0].strip() if docstring else None
            params = [
                a.arg for a in node.args.args if a.arg not in ("self", "cls")
            ]
            tools.append(ADKToolInfo(
                name=node.name,
                description=description,
                parameters=params,
                file=path,
                line=node.lineno,
                is_adk_decorated=is_decorated,
            ))
    return tools


def _extract_entry_points(metadata: dict[str, Any]) -> list[ADKEntryPoint]:
    scripts = metadata.get("scripts", {})
    return [ADKEntryPoint(command=cmd, target=target) for cmd, target in scripts.items()]


def _extract_cli_commands(py_files: list[Path]) -> list[ADKCliCommand]:
    """Find Typer @app.command() decorated functions."""
    commands: list[ADKCliCommand] = []
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for decorator in node.decorator_list:
                dname = _full_decorator_name(decorator)
                if "command" in dname:
                    docstring = ast.get_docstring(node)
                    desc = docstring.splitlines()[0].strip() if docstring else None
                    commands.append(ADKCliCommand(
                        name=node.name,
                        description=desc,
                        file=path,
                    ))
    return commands


def _full_decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Attribute):
        return f"{_full_decorator_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return _full_decorator_name(node.func)
    return ""


def _extract_env_vars(root: Path, py_files: list[Path]) -> dict[str, set[str]]:
    variables: dict[str, set[str]] = {}
    for env_file in [root / ".env.example", root / ".env"]:
        if not env_file.exists():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*([A-Z_][A-Z0-9_]*)\s*=", line)
            if match:
                variables.setdefault(match.group(1), set()).add(env_file.name)
    for path in py_files:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in [
            r"os\.getenv\(\s*['\"]([A-Z_][A-Z0-9_]*)['\"]",
            r"os\.environ\[\s*['\"]([A-Z_][A-Z0-9_]*)['\"]\s*\]",
            r"os\.environ\.get\(\s*['\"]([A-Z_][A-Z0-9_]*)['\"]",
        ]:
            for match in re.finditer(pattern, text):
                rel = str(path.relative_to(root))
                variables.setdefault(match.group(1), set()).add(rel)
    return dict(sorted(variables.items()))


def _extract_pydantic_models(py_files: list[Path]) -> list[str]:
    models: list[str] = []
    pydantic_bases = {"BaseModel", "RootModel"}
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = {_base_name(b) for b in node.bases}
                if bases & pydantic_bases:
                    models.append(node.name)
    return models


def _extract_llm_providers(py_files: list[Path], root: Path) -> list[str]:
    providers: set[str] = set()
    patterns = {
        r"openai": "OpenAI",
        r"litellm": "LiteLLM",
        r"anthropic": "Anthropic",
        r"google\.generativeai|google-generativeai|gemini": "Google Gemini",
        r"vertexai|vertex_ai": "Vertex AI",
        r"bedrock": "AWS Bedrock",
        r"azure_openai|AzureOpenAI": "Azure OpenAI",
    }
    for path in py_files:
        try:
            text = path.read_text(encoding="utf-8").lower()
        except Exception:
            continue
        for pattern, label in patterns.items():
            if re.search(pattern, text):
                providers.add(label)
    return sorted(providers)


def _read_pyproject(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return {}
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        result = data.get("project", {})
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}
