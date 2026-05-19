from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

_queue: asyncio.Queue | None = None


def set_queue(q: asyncio.Queue) -> None:
    global _queue
    _queue = q


def emit(event: dict[str, Any]) -> None:
    if _queue is not None:
        try:
            _queue.put_nowait({**event, "ts": datetime.now().isoformat()})
        except asyncio.QueueFull:
            pass


def _agent_key(role: str) -> str:
    return role.lower().replace(" ", "_")


def patch_crewai() -> bool:
    try:
        from crewai import Agent, Crew
    except ImportError:
        return False

    # ── Patch Agent.execute_task ─────────────────────────────────────────────
    original_execute = Agent.execute_task

    def patched_execute(self, task, context=None, tools=None):
        key = _agent_key(self.role)
        emit({
            "type": "task_start",
            "agent": self.role,
            "agent_key": key,
            "task": (task.description or "")[:100],
        })

        orig_step = self.step_callback

        def _step(step_output):
            text = str(step_output)[:300] if step_output else ""
            emit({
                "type": "agent_thinking",
                "agent": self.role,
                "agent_key": key,
                "text": text,
            })
            if orig_step:
                orig_step(step_output)

        self.step_callback = _step
        result = original_execute(self, task, context=context, tools=tools)
        self.step_callback = orig_step

        emit({
            "type": "task_done",
            "agent": self.role,
            "agent_key": key,
            "task": (task.description or "")[:100],
            "output": str(result)[:400] if result else "",
        })
        return result

    Agent.execute_task = patched_execute

    # ── Patch Crew.kickoff ───────────────────────────────────────────────────
    original_kickoff = Crew.kickoff

    def patched_kickoff(self, inputs=None):
        emit({
            "type": "crew_start",
            "process": str(self.process) if self.process else "sequential",
            "agents": [{"name": a.role, "key": _agent_key(a.role)} for a in self.agents],
            "tasks": [
                {
                    "description": (t.description or "")[:80],
                    "agent": t.agent.role if t.agent else None,
                }
                for t in self.tasks
            ],
        })
        result = original_kickoff(self, inputs=inputs)
        emit({
            "type": "crew_done",
            "result": str(result)[:600] if result else "",
        })
        return result

    Crew.kickoff = patched_kickoff
    return True
