# Play Interface

The Play UI is organized around three regions:

| Region | Purpose |
| --- | --- |
| Left roster | Agent list, colors, names, status, and quick identity |
| Center city | Animated pixel-art environment with agents and the Tool Hub |
| Right activity panel | Timeline, thoughts, tools, communications, and raw logs |

## Controls

| Control | Behavior |
| --- | --- |
| START | Launches the project run |
| STOP | Terminates the active run without closing the UI |
| RESTART | Starts a fresh run after a run has started |

STOP terminates the child process started by `lantern play`. On Unix-like systems AgentLantern starts the child in its own process group so related subprocesses can be stopped together.

## Agents

Each agent is displayed with:

- a pixel-art avatar,
- the agent name below the avatar,
- a persistent thought bubble above the avatar,
- an activity badge for task, thinking, tool, delegation, completion, or error state.

When an agent is thinking, the bubble displays `...` until the next thought or task event arrives.

## Activity Panels

| Panel | Content |
| --- | --- |
| Timeline | Chronological event stream |
| Thoughts | Captured agent thoughts and reasoning snippets |
| Tools | External tool calls, inputs, and associated agents |
| Comms | Delegation and coworker questions |
| Log | Raw stdout and runner messages |

Clicking an agent opens its detail panel with event history and completed work.

## Final Report

If the run finishes successfully and `report.md` exists in the project root, AgentLantern reads it and displays it in the UI.

This is common in CrewAI projects with:

```yaml
output_file: report.md
```
