from __future__ import annotations

import asyncio
import http.server
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import websockets
    import websockets.server
    _HAS_WS = True
except ImportError:
    _HAS_WS = False

_UI_DIR   = Path(__file__).parent / "play_ui"
_WS_PORT  = 7890
_HTTP_PORT = 7891

# ── Hook script injected into the user's subprocess ──────────────────────────
# This runs inside the user's venv — NO agentlantern imports allowed.
_HOOK_SCRIPT = '''\
import os as _os, json as _json
from datetime import datetime as _dt

def _fd_write(line):
    try:
        _os.write(1, (line + "\\n").encode("utf-8", errors="replace"))
    except Exception:
        pass

_fd_write("LANTERN_EVENT:" + _json.dumps({"type":"hook_loaded","ts":_dt.now().isoformat()}))

import json, os
from datetime import datetime
from pathlib import Path

def _load_dotenv():
    env_file = Path(os.getcwd()) / ".env"
    if not env_file.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=False)
        return
    except ImportError:
        pass
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)

_load_dotenv()

def _emit(event):
    event["ts"] = datetime.now().isoformat()
    _fd_write("LANTERN_EVENT:" + json.dumps(event, ensure_ascii=False))

def _key(role):
    if not role:
        return "agent"
    return role.strip().lower().replace(" ", "_").replace("-", "_")

import time as _time_mod
_orig_sleep = _time_mod.sleep
_crew_started = [False]

def _fast_sleep(secs):
    if not _crew_started[0] and secs > 0.1:
        return _orig_sleep(0.05)
    return _orig_sleep(secs)

_time_mod.sleep = _fast_sleep

# Shared state: currently executing agent role (sequential crews)
_active_agent = [None]

def _extract_thought(output):
    """Pull readable text from various step output formats."""
    if output is None:
        return ""
    if isinstance(output, str):
        text = output
    else:
        text = ""
        for attr in ("log", "text", "output", "content", "thought"):
            val = getattr(output, attr, None)
            if val:
                text = str(val) if not isinstance(val, str) else val
                break
        if not text:
            text = str(output)
    # Extract just the "Thought:" portion when present (LangChain format)
    if "Thought:" in text:
        part = text.split("Thought:", 1)[1]
        if "Action:" in part:
            part = part.split("Action:", 1)[0]
        return part.strip()[:500]
    return text.strip()[:500]


def _patch_crewai():
    try:
        from crewai import Crew
    except ImportError:
        _emit({"type": "debug", "msg": "crewai not importable"}); return
    except Exception as exc:
        _emit({"type": "debug", "msg": f"crewai import error: {exc}"}); return

    _emit({"type": "debug", "msg": "crewai imported — installing patches"})

    # ── 1. Task.execute_sync  (CrewAI >= 1.0) — tracks which agent is active ──
    try:
        from crewai import Task
        orig_exec_sync = getattr(Task, "execute_sync", None)
        if orig_exec_sync:
            def _exec_sync(self, agent, context=None, tools=None):
                role = (getattr(agent, "role", "agent") or "agent").strip() if agent else "agent"
                prev = _active_agent[0]          # save caller's context (for nested delegation)
                _active_agent[0] = role
                _emit({"type": "task_start", "agent": role, "agent_key": _key(role),
                       "task": (self.description or "")[:120]})
                try:
                    result = orig_exec_sync(self, agent, context=context, tools=tools)
                except Exception as exc:
                    _emit({"type": "task_error", "agent": role, "error": str(exc)[:300]})
                    raise
                finally:
                    _active_agent[0] = prev      # restore caller (not None)
                raw = str(getattr(result, "raw", result))[:500] if result else ""
                _emit({"type": "task_done", "agent": role, "agent_key": _key(role),
                       "task": (self.description or "")[:120], "output": raw})
                return result
            Task.execute_sync = _exec_sync
            _emit({"type": "debug", "msg": "Task.execute_sync patched"})
    except Exception as exc:
        _emit({"type": "debug", "msg": f"Task.execute_sync patch: {exc}"})

    # ── 2. Agent.execute_task  (CrewAI < 1.0) ──────────────────────────────────
    try:
        from crewai import Agent
        orig_execute = getattr(Agent, "execute_task", None)
        if orig_execute:
            def _execute(self, task, context=None, tools=None):
                role = (self.role or "agent").strip()
                prev = _active_agent[0]
                _active_agent[0] = role
                _emit({"type": "task_start", "agent": role, "agent_key": _key(role),
                       "task": (getattr(task, "description", None) or str(task))[:120]})
                result = orig_execute(self, task, context=context, tools=tools)
                _active_agent[0] = prev
                _emit({"type": "task_done", "agent": role, "agent_key": _key(role),
                       "task": (getattr(task, "description", None) or str(task))[:120],
                       "output": str(result)[:400] if result else ""})
                return result
            Agent.execute_task = _execute
            _emit({"type": "debug", "msg": "Agent.execute_task patched"})
    except Exception as exc:
        _emit({"type": "debug", "msg": f"Agent.execute_task patch: {exc}"})

    # ── 3. Delegation tools ────────────────────────────────────────────────────
    def _patch_delegation_tools():
        # CrewAI 0.x: DelegateWork / AskQuestion
        # CrewAI 1.x+: DelegateWorkTool / AskQuestionTool
        pairs = [
            ("DelegateWorkTool", "DelegateWork", True),
            ("AskQuestionTool",  "AskQuestion",  False),
        ]
        patched = 0
        for mod_path in ["crewai.tools.agent_tools.agent_tools",
                          "crewai.tools.agent_tools", "crewai.tools"]:
            try:
                import importlib
                mod = importlib.import_module(mod_path)
                for new_name, old_name, is_del in pairs:
                    cls = getattr(mod, new_name, None) or getattr(mod, old_name, None)
                    if cls is None:
                        continue
                    orig_run = getattr(cls, "_run", None)
                    if orig_run is None:
                        continue

                    def _make_patch(orig, is_delegate):
                        def _p(self, *args, **kwargs):
                            role = (_active_agent[0] or "unknown").strip()
                            # Resolve coworker: keyword or positional arg[2]
                            coworker = str(kwargs.get("coworker") or
                                           (args[2] if len(args) > 2 else "") or "").strip()
                            content  = str(kwargs.get("task") or kwargs.get("question") or
                                           (args[0] if args else "") or "")[:400]
                            ctx      = str(kwargs.get("context") or
                                           (args[1] if len(args) > 1 else "") or "")[:200]
                            ev = "agent_delegate" if is_delegate else "agent_question"
                            _emit({"type": ev,
                                   "from_agent": role, "from_agent_key": _key(role),
                                   "to_agent": coworker, "to_agent_key": _key(coworker),
                                   "content": content, "context": ctx})
                            result = orig(self, *args, **kwargs)
                            _emit({"type": ev + "_result",
                                   "from_agent": role, "to_agent": coworker,
                                   "result": str(result)[:400] if result else ""})
                            return result
                        return _p

                    cls._run = _make_patch(orig_run, is_del)
                    patched += 1
                    _emit({"type": "debug", "msg": f"patched {new_name or old_name}._run"})
                if patched:
                    break
            except ImportError:
                pass
            except Exception as exc:
                _emit({"type": "debug", "msg": f"delegation patch {mod_path}: {exc}"})

        if not patched:
            # Fallback: patch BaseTool._run to catch all tool calls by name
            try:
                try:
                    from langchain_core.tools import BaseTool
                except ImportError:
                    from langchain.tools import BaseTool  # type: ignore
                orig_bt = BaseTool._run

                def _bt(self, *args, **kwargs):
                    tname = (getattr(self, "name", "") or "").lower()
                    role  = (_active_agent[0] or "unknown").strip()
                    inp   = str(args[0] if args else kwargs)[:300]
                    if "delegate" in tname:
                        cw = str(kwargs.get("coworker","") or (args[2] if len(args)>2 else ""))
                        _emit({"type": "agent_delegate",
                               "from_agent": role, "from_agent_key": _key(role),
                               "to_agent": cw, "to_agent_key": _key(cw), "content": inp})
                    elif "ask" in tname or "question" in tname:
                        cw = str(kwargs.get("coworker","") or (args[2] if len(args)>2 else ""))
                        _emit({"type": "agent_question",
                               "from_agent": role, "from_agent_key": _key(role),
                               "to_agent": cw, "to_agent_key": _key(cw), "content": inp})
                    else:
                        _emit({"type": "agent_tool", "agent": role, "agent_key": _key(role),
                               "tool": getattr(self,"name","?"), "input": inp})
                    return orig_bt(self, *args, **kwargs)

                BaseTool._run = _bt
                _emit({"type": "debug", "msg": "BaseTool._run patched (fallback)"})
            except Exception as exc:
                _emit({"type": "debug", "msg": f"BaseTool fallback: {exc}"})

    _patch_delegation_tools()

    # ── 4. Generic CrewAI tools ───────────────────────────────────────────────
    try:
        from crewai.tools import BaseTool as _CrewBaseTool
        _orig_tool_run = _CrewBaseTool.run

        def _tool_run(self, *args, **kwargs):
            role = (_active_agent[0] or "unknown").strip()
            name = str(getattr(self, "name", "") or getattr(self, "__class__", type(self)).__name__)
            low = name.lower()
            if not any(word in low for word in ("delegate", "ask", "question")):
                inp = str(args[0] if args else kwargs)[:300]
                _emit({"type": "agent_tool", "agent": role, "agent_key": _key(role),
                       "tool": name, "input": inp})
            return _orig_tool_run(self, *args, **kwargs)

        _CrewBaseTool.run = _tool_run
        _emit({"type": "debug", "msg": "CrewAI BaseTool.run patched"})
    except Exception as exc:
        _emit({"type": "debug", "msg": f"CrewAI BaseTool.run patch: {exc}"})

    # ── 5. Try CrewAI 1.x event bus for LLM-level thought capture ─────────────
    def _try_event_bus():
        try:
            import importlib
            em = importlib.import_module("crewai.utilities.events")
            bus = getattr(em, "crewai_event_bus", None)
            if bus is None:
                return
            # Subscribe to any LLM completed / agent step event
            for attr in dir(em):
                obj = getattr(em, attr)
                if not (isinstance(obj, type)):
                    continue
                alow = attr.lower()
                if ("llm" in alow and "complet" in alow) or ("agent" in alow and "step" in alow):
                    try:
                        @bus.on(obj)
                        def _on_llm(source, event, _cls=obj):
                            try:
                                role = (_active_agent[0] or
                                        getattr(source, "role", None) or "agent")
                                resp = (getattr(event, "response", None) or
                                        getattr(event, "output", None) or
                                        getattr(event, "content", None) or "")
                                if resp:
                                    thought = _extract_thought(str(resp))
                                    if thought:
                                        _emit({"type": "agent_thought", "agent": role,
                                               "agent_key": _key(role), "thought": thought})
                            except Exception:
                                pass
                        _emit({"type": "debug", "msg": f"event_bus: subscribed to {attr}"})
                    except Exception:
                        pass
        except Exception as exc:
            _emit({"type": "debug", "msg": f"event_bus: {exc}"})

    _try_event_bus()

    # ── 6. Crew.kickoff  (+ async + for_each) — crew lifecycle + step capture ──
    import re as _re

    orig_kickoff = Crew.kickoff

    def _kickoff(self, inputs=None):
        _crew_started[0] = True
        _time_mod.sleep = _orig_sleep

        # Helper: fill {placeholders} in role names using kickoff inputs
        def _fill(name):
            if not name:
                return ""
            name = name.strip()
            if inputs and '{' in name:
                try:
                    return name.format(**inputs)
                except Exception:
                    return _re.sub(r'\\{[^}]+\\}', '?', name)
            return name

        # Inject step_callback to capture agent thoughts from LangChain steps
        orig_step_cb = getattr(self, "step_callback", None)

        def _step(output):
            try:
                role = _active_agent[0] or "agent"
                thought = _extract_thought(output)
                if thought:
                    _emit({"type": "agent_thought", "agent": role,
                           "agent_key": _key(role), "thought": thought})
                # Also detect tool use from AgentAction
                tname = getattr(output, "tool", None)
                if tname:
                    tinput = str(getattr(output, "tool_input", ""))[:300]
                    tl = str(tname).lower()
                    if "delegate" in tl:
                        coworker = ""
                        if isinstance(getattr(output, "tool_input", None), dict):
                            coworker = str(output.tool_input.get("coworker", ""))
                        _emit({"type": "agent_delegate",
                               "from_agent": role, "from_agent_key": _key(role),
                               "to_agent": coworker, "to_agent_key": _key(coworker),
                               "content": tinput})
                    elif "ask" in tl or "question" in tl:
                        _emit({"type": "agent_question",
                               "from_agent": role, "from_agent_key": _key(role),
                               "to_agent": "", "content": tinput})
                    else:
                        _emit({"type": "agent_tool", "agent": role,
                               "agent_key": _key(role), "tool": str(tname), "input": tinput})
            except Exception:
                pass
            if orig_step_cb:
                orig_step_cb(output)

        self.step_callback = _step

        try:
            _emit({
                "type": "crew_start",
                "process": str(self.process) if hasattr(self, "process") else "sequential",
                "agents": [{"name": _fill(a.role), "key": _key(_fill(a.role))} for a in (self.agents or [])],
                "tasks": [{"description": (t.description or "")[:80],
                           "agent": _fill(t.agent.role) if (t.agent if hasattr(t, "agent") else None) else None}
                          for t in (self.tasks or [])],
            })
        except Exception as exc:
            _emit({"type": "debug", "msg": f"crew_start emit: {exc}"})

        try:
            result = orig_kickoff(self, inputs=inputs)
        except Exception as exc:
            _emit({"type": "error", "message": f"Crew.kickoff raised: {exc}"}); raise

        _emit({"type": "crew_done", "result": str(result)[:600] if result else ""})
        return result

    Crew.kickoff = _kickoff

    orig_kickoff_async = getattr(Crew, "kickoff_async", None)
    if orig_kickoff_async:
        async def _kickoff_async(self, inputs=None):
            _crew_started[0] = True
            _time_mod.sleep = _orig_sleep
            try:
                _emit({
                    "type": "crew_start",
                    "process": str(self.process) if hasattr(self, "process") else "sequential",
                    "agents": [{"name": a.role, "key": _key(a.role)} for a in (self.agents or [])],
                    "tasks": [{"description": (t.description or "")[:80],
                               "agent": (t.agent.role if t.agent else None)
                                        if hasattr(t, "agent") else None}
                              for t in (self.tasks or [])],
                })
            except Exception as exc:
                _emit({"type": "debug", "msg": f"crew_start async: {exc}"})
            try:
                result = await orig_kickoff_async(self, inputs=inputs)
            except Exception as exc:
                _emit({"type": "error", "message": f"kickoff_async: {exc}"}); raise
            _emit({"type": "crew_done", "result": str(result)[:600] if result else ""})
            return result
        Crew.kickoff_async = _kickoff_async

    orig_kickoff_for_each = getattr(Crew, "kickoff_for_each", None)
    if orig_kickoff_for_each:
        def _kickoff_for_each(self, inputs):
            _crew_started[0] = True
            _time_mod.sleep = _orig_sleep
            _emit({"type": "crew_start", "process": "for_each",
                   "agents": [{"name": a.role, "key": _key(a.role)} for a in (self.agents or [])],
                   "tasks": []})
            result = orig_kickoff_for_each(self, inputs)
            _emit({"type": "crew_done", "result": str(result)[:600] if result else ""})
            return result
        Crew.kickoff_for_each = _kickoff_for_each

    _emit({"type": "debug", "msg": "all patches complete"})

try:
    _patch_crewai()
except Exception as _exc:
    try:
        _emit({"type": "debug", "msg": f"_patch_crewai raised: {_exc}"})
    except Exception:
        pass
'''


# ── Project entry-point detection ─────────────────────────────────────────────

def _detect_cmd(root: Path) -> list[str]:
    """Return the command list to run the project via uv.

    We intentionally avoid `crewai run` because it spawns a second subprocess
    that breaks our PYTHONPATH/sitecustomize.py injection.  Instead we invoke
    the declared entry-point script directly so everything runs in a single
    Python process that inherits our env.
    """
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            scripts = data.get("project", {}).get("scripts", {})
            # Prefer well-known crew entry points (run directly, not via crewai run)
            for name in ("run_crew", "run", "main"):
                if name in scripts:
                    return ["uv", "run", name]
            # Any other script is fine too
            if scripts:
                return ["uv", "run", next(iter(scripts))]
        except Exception:
            pass

    for candidate in ["main.py", "run.py"]:
        if (root / candidate).exists():
            return ["uv", "run", "python", candidate]

    return ["uv", "run", "python", "-m", root.name]


# ── Subprocess runner ─────────────────────────────────────────────────────────

def _run_subprocess(root: Path, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
    cmd = _detect_cmd(root)

    # Write sitecustomize.py to a tmpdir — Python auto-imports it at startup
    tmpdir = tempfile.mkdtemp(prefix="lantern_play_")
    (Path(tmpdir) / "sitecustomize.py").write_text(_HOOK_SCRIPT, encoding="utf-8")

    # Prepend tmpdir to PYTHONPATH so sitecustomize.py is found first
    existing_pypath = os.environ.get("PYTHONPATH", "")
    pythonpath = tmpdir + (":" + existing_pypath if existing_pypath else "")
    env = {**os.environ, "PYTHONPATH": pythonpath}

    _replay_buf: list[dict[str, Any]] = []
    my_seq = _play_state["run_seq"]   # capture at start; drop events if seq changed

    def _emit_ev(ev: dict[str, Any]) -> None:
        if _play_state["run_seq"] != my_seq:
            return   # stale — a new run was started, discard
        ev.setdefault("ts", datetime.now().isoformat())
        _replay_buf.append({**ev})
        asyncio.run_coroutine_threadsafe(queue.put(ev), loop)

    _emit_ev({"type": "runner_info", "message": f"Running: {' '.join(cmd)}"})

    try:
        proc = subprocess.Popen(
            cmd, cwd=str(root), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
            start_new_session=(os.name != "nt"),
        )
        _play_state["proc"] = proc
        for line in proc.stdout:  # type: ignore
            line = line.rstrip()
            if line.startswith("LANTERN_EVENT:"):
                try:
                    ev = json.loads(line[len("LANTERN_EVENT:"):])
                    _emit_ev(ev)
                except json.JSONDecodeError:
                    pass
            elif line:
                _emit_ev({"type": "stdout", "text": line})
        proc.wait()
        report_path = root / "report.md"
        if proc.returncode == 0 and report_path.exists():
            try:
                report = report_path.read_text(encoding="utf-8", errors="replace")
                _emit_ev({
                    "type": "final_report",
                    "path": str(report_path),
                    "content": report[:20000],
                })
            except Exception as exc:
                _emit_ev({"type": "error", "message": f"Could not read report.md: {exc}"})
        _emit_ev({"type": "runner_info", "message": "Process finished."})

        # Auto-save replay if a name was provided with this run
        replay_name = _play_state.get("replay_name", "").strip()
        if replay_name:
            try:
                replays_dir = root / ".lantern_replays"
                replays_dir.mkdir(exist_ok=True)
                replay_file = replays_dir / f"{replay_name}.jsonl"
                with replay_file.open("w", encoding="utf-8") as f:
                    for recorded in _replay_buf:
                        f.write(json.dumps(recorded, ensure_ascii=False) + "\n")
                _emit_ev({
                    "type": "replay_saved",
                    "name": replay_name,
                    "path": str(replay_file),
                    "count": len(_replay_buf),
                })
            except Exception as exc:
                _emit_ev({"type": "error", "message": f"Could not save replay: {exc}"})

    except Exception as exc:
        _emit_ev({"type": "error", "message": str(exc)})


def _emit_from_thread(queue: asyncio.Queue, loop: asyncio.AbstractEventLoop, event: dict[str, Any]) -> None:
    event.setdefault("ts", datetime.now().isoformat())
    asyncio.run_coroutine_threadsafe(queue.put(event), loop)


# ── HTTP server for the frontend ──────────────────────────────────────────────

def _serve_frontend(port: int) -> None:
    os.chdir(_UI_DIR)
    class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

        def log_message(self, *args: Any) -> None:
            return

    handler = NoCacheHandler
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()


# ── WebSocket broadcast ───────────────────────────────────────────────────────

_clients: set = set()
_event_history: list[str] = []   # replay buffer for late-joining browsers
_MAX_HISTORY = 500
_play_state: dict[str, Any] = {"proc": None, "run_seq": 0}   # tracks current subprocess


async def _broadcaster(queue: asyncio.Queue) -> None:
    while True:
        event = await queue.get()
        payload = json.dumps(event, ensure_ascii=False)
        _event_history.append(payload)
        if len(_event_history) > _MAX_HISTORY:
            _event_history.pop(0)
        dead = set()
        for ws in list(_clients):
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        _clients.difference_update(dead)


# ── Entry point ───────────────────────────────────────────────────────────────

def run_play(project_root: Path, ws_port: int = _WS_PORT, http_port: int = _HTTP_PORT, name: str = "") -> None:
    if not _HAS_WS:
        print("AgentLantern Play requires websockets — run: pip install agentlantern")
        sys.exit(1)

    root = project_root.resolve()
    if not root.exists():
        print(f"Project path not found: {root}")
        sys.exit(1)

    import re as _re
    from agentlantern.frameworks.registry import detect_framework
    analyzer = detect_framework(root)
    framework = analyzer.framework_name

    # Static analysis — extract agents before the crew runs
    _static_agents: list[dict[str, Any]] = []
    try:
        project = analyzer.analyze(root)
        if hasattr(project, "agent_methods"):
            for method_name, method in project.agent_methods.items():
                yaml_key = getattr(method, "config_key", None) or method_name
                role = ""
                if hasattr(project, "agents"):
                    role = (project.agents.get(yaml_key) or {}).get("role", "") or ""
                role = _re.sub(r"\{[^}]+\}", "", role).strip()
                if not role:
                    role = method_name.replace("_", " ").title()
                key = method_name.lower().replace(" ", "_").replace("-", "_")
                _static_agents.append({"name": role, "key": key})
    except Exception:
        pass
    _play_state["static_agents"] = _static_agents
    _play_state["framework"] = framework
    if name:
        _play_state["replay_name"] = name.strip()

    queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

    # HTTP frontend
    threading.Thread(target=_serve_frontend, args=(http_port,), daemon=True).start()

    print(f"\n  AgentLantern Play — {root.name} ({framework})")
    print(f"  UI  → http://127.0.0.1:{http_port}?project={root.name}&framework={framework}&ws={ws_port}")
    print(f"  WS  → ws://127.0.0.1:{ws_port}")
    print()

    async def _main() -> None:
        loop = asyncio.get_event_loop()

        def _start_crew() -> None:
            """Kill current subprocess (if any) and start a fresh run."""
            # Increment seq first — any events still in the queue from the old
            # subprocess will be silently dropped by _run_subprocess._emit_ev.
            _play_state["run_seq"] = _play_state.get("run_seq", 0) + 1
            p = _play_state.get("proc")
            if p and p.poll() is None:
                try:
                    if os.name != "nt":
                        os.killpg(p.pid, signal.SIGKILL)
                    else:
                        p.kill()
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
                try:
                    p.wait(timeout=3)
                except Exception:
                    pass
            _event_history.clear()
            _emit_from_thread(queue, loop, {"type": "crew_reset"})
            threading.Thread(
                target=_run_subprocess,
                args=(root, queue, loop),
                daemon=True,
            ).start()

        def _stop_crew() -> None:
            """Stop the active crew subprocess without clearing the UI."""
            p = _play_state.get("proc")
            if not p or p.poll() is not None:
                _emit_from_thread(queue, loop, {
                    "type": "runner_info",
                    "message": "No active crew process to stop.",
                })
                return
            # Increment seq so any queued events from this run are discarded
            _play_state["run_seq"] = _play_state.get("run_seq", 0) + 1
            _emit_from_thread(queue, loop, {"type": "crew_stopping"})
            try:
                if os.name == "nt":
                    p.terminate()
                else:
                    os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=1)   # give 1 s for graceful shutdown
            except Exception:
                pass
            # Force kill if still alive
            if p.poll() is None:
                try:
                    if os.name != "nt":
                        os.killpg(p.pid, signal.SIGKILL)
                    else:
                        p.kill()
                except Exception:
                    pass
                try:
                    p.wait(timeout=2)
                except Exception:
                    pass
            _emit_from_thread(queue, loop, {"type": "crew_stopped"})

        async def _ws_handler_local(websocket) -> None:
            # Send static crew info only when no live run has started yet
            static_agents = _play_state.get("static_agents", [])
            crew_started = any(
                json.loads(p).get("type") == "crew_start"
                for p in _event_history
            )
            if static_agents and not crew_started:
                try:
                    await websocket.send(json.dumps({
                        "type": "static_crew_info",
                        "agents": static_agents,
                        "framework": _play_state.get("framework", ""),
                        "ts": datetime.now().isoformat(),
                    }))
                except Exception:
                    return
            for payload in list(_event_history):
                try:
                    await websocket.send(payload)
                except Exception:
                    return
            _clients.add(websocket)
            try:
                async for message in websocket:
                    try:
                        cmd_data = json.loads(message)
                        if cmd_data.get("type") == "start_crew":
                            _play_state["replay_name"] = str(cmd_data.get("name", "")).strip()
                            threading.Thread(target=_start_crew, daemon=True).start()
                        elif cmd_data.get("type") == "stop_crew":
                            threading.Thread(target=_stop_crew, daemon=True).start()
                    except Exception:
                        pass
            finally:
                _clients.discard(websocket)

        # Open browser
        async def _open():
            await asyncio.sleep(1.2)
            extra = f"&autostart=1&name={urllib.parse.quote(name)}" if name else ""
            webbrowser.open(
                f"http://127.0.0.1:{http_port}"
                f"?project={root.name}&framework={framework}&ws={ws_port}{extra}"
            )
        asyncio.create_task(_open())

        # If --name was provided, auto-start immediately for new connections.
        # Otherwise the browser asks for a run/replay name before START.
        if name:
            threading.Thread(target=_start_crew, daemon=True).start()

        _emit_from_thread(queue, loop, {
            "type": "runner_info",
            "message": "Ready. Click START to launch the crew.",
        })

        # Start WebSocket server + broadcaster
        async with websockets.server.serve(_ws_handler_local, "127.0.0.1", ws_port):
            await _broadcaster(queue)

    asyncio.run(_main())


# ── Replay ────────────────────────────────────────────────────────────────────

def run_replay(
    replay_path: Path,
    speed: float = 1.0,
    ws_port: int = _WS_PORT,
    http_port: int = _HTTP_PORT,
) -> None:
    if not _HAS_WS:
        print("AgentLantern Play requires websockets — run: pip install agentlantern")
        sys.exit(1)

    if not replay_path.exists():
        print(f"\n  Error: replay not found — {replay_path}")
        replays_dir = Path(".lantern_replays")
        if replays_dir.exists():
            available = sorted(replays_dir.glob("*.jsonl"))
            if available:
                print(f"\n  Available replays in {replays_dir}/:")
                for r in available:
                    size = r.stat().st_size
                    lines = sum(1 for _ in r.open())
                    print(f"    lantern replay {r.stem:<30}  ({lines} events, {size//1024} KB)")
            else:
                print(f"\n  No replays found in {replays_dir}/")
        else:
            print(
                "\n  No .lantern_replays/ directory found in the current directory.\n"
                "  Run 'lantern play .' and enter a replay name before clicking START."
            )
        print()
        sys.exit(1)

    events: list[dict[str, Any]] = []
    with replay_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    replay_name = replay_path.stem

    threading.Thread(target=_serve_frontend, args=(http_port,), daemon=True).start()

    print(f"\n  AgentLantern Replay — {replay_name} ({len(events)} events, speed ×{speed})")
    print(f"  UI  → http://127.0.0.1:{http_port}?replay=1&name={replay_name}&ws={ws_port}")
    print(f"  WS  → ws://127.0.0.1:{ws_port}")
    print()

    async def _replay_handler(websocket) -> None:
        # Mutable control state shared between playback loop and control listener
        paused   = asyncio.Event()
        paused.set()          # set = not paused → loop can proceed
        cur_speed = [speed]   # mutable so the control listener can update it
        stopped  = [False]

        restart  = [False]
        seek_to  = [-1]    # -1 = no pending seek

        async def _listen_controls() -> None:
            try:
                async for msg in websocket:
                    try:
                        cmd = json.loads(msg)
                        t = cmd.get("type", "")
                        if t == "replay_pause":
                            paused.clear()
                        elif t == "replay_resume":
                            paused.set()
                        elif t == "replay_speed":
                            cur_speed[0] = max(0.1, float(cmd.get("value", 1.0)))
                        elif t == "replay_stop":
                            stopped[0] = True
                            paused.set()
                        elif t == "replay_restart":
                            seek_to[0] = 0
                            restart[0] = True
                            stopped[0] = False
                            paused.set()
                        elif t == "replay_seek":
                            seek_to[0] = max(0, min(total - 1, int(cmd.get("position", 0))))
                            restart[0] = True
                            paused.set()
                    except Exception:
                        pass
            except Exception:
                pass

        asyncio.create_task(_listen_controls())

        total = len(events)

        async def _play_once(start_from: int = 0) -> None:
            """Play all events once, fast-forwarding to start_from without delays."""
            await websocket.send(json.dumps({
                "type": "crew_reset",
                "replay_total": total,
                "ts": datetime.now().isoformat(),
            }))
            prev_ts: datetime | None = None
            for idx, ev in enumerate(events):
                if stopped[0] or restart[0]:
                    return

                if idx < start_from:
                    # Fast-forward: send instantly, no inter-event delay
                    try:
                        await websocket.send(json.dumps(ev, ensure_ascii=False))
                    except Exception:
                        return
                    # Emit progress once at the seek target
                    if idx + 1 == start_from:
                        try:
                            await websocket.send(json.dumps({
                                "type": "replay_progress",
                                "current": start_from,
                                "total": total,
                                "ts": datetime.now().isoformat(),
                            }))
                        except Exception:
                            return
                    continue

                # Normal timing
                ts_str = ev.get("ts")
                if ts_str and prev_ts:
                    try:
                        curr = datetime.fromisoformat(ts_str)
                        raw_delay = min((curr - prev_ts).total_seconds(), 10.0)
                        elapsed = 0.0
                        while elapsed < raw_delay and not stopped[0] and not restart[0]:
                            await paused.wait()
                            chunk = min(0.05, raw_delay - elapsed)
                            await asyncio.sleep(chunk / max(cur_speed[0], 0.1))
                            elapsed += chunk
                    except Exception:
                        pass
                if ts_str:
                    try:
                        prev_ts = datetime.fromisoformat(ts_str)
                    except Exception:
                        pass
                if stopped[0] or restart[0]:
                    return

                try:
                    await websocket.send(json.dumps(ev, ensure_ascii=False))
                except Exception:
                    return

                if (idx + 1) % 10 == 0 or idx + 1 == total:
                    try:
                        await websocket.send(json.dumps({
                            "type": "replay_progress",
                            "current": idx + 1,
                            "total": total,
                            "ts": datetime.now().isoformat(),
                        }))
                    except Exception:
                        return

            if not stopped[0] and not restart[0]:
                try:
                    await websocket.send(json.dumps({
                        "type": "replay_done",
                        "name": replay_name,
                        "count": total,
                        "ts": datetime.now().isoformat(),
                    }))
                except Exception:
                    pass

        # Main loop — restarts or seeks when requested
        while not stopped[0]:
            start = seek_to[0] if seek_to[0] >= 0 else 0
            seek_to[0] = -1
            restart[0] = False
            await _play_once(start_from=start)
            if not restart[0]:
                break

        # Keep connection alive so the UI stays visible
        try:
            await asyncio.Future()
        except Exception:
            pass

    async def _main_replay() -> None:
        async def _open() -> None:
            await asyncio.sleep(1.2)
            webbrowser.open(
                f"http://127.0.0.1:{http_port}"
                f"?replay=1&name={replay_name}&ws={ws_port}"
            )
        asyncio.create_task(_open())

        async with websockets.server.serve(_replay_handler, "127.0.0.1", ws_port):
            await asyncio.Future()

    asyncio.run(_main_replay())
