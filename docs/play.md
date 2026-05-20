# lantern play

`lantern play` is AgentLantern's live runtime viewer. It runs a supported agent project and opens a pixel-art UI where you can watch agents work, think, delegate, call tools, and produce a final report.

<div class="youtube-embed">
  <iframe
    src="https://www.youtube.com/embed/Rklr86AiKuk"
    title="AgentLantern lantern play demo"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen
  ></iframe>
</div>

Use this section when you want to:

- launch a supported agent project from the UI,
- understand the Play interface,
- verify how agents are placed in the world,
- inspect tool calls through the Tool Hub,
- save and replay a run,
- debug why a run or UI does not update.

> `lantern play` executes the target project. The project can call LLM providers, APIs, files, tools, and network services configured by that project.

## Pages

| Page | Use it for |
| --- | --- |
| [Quick Start](play/quick-start.md) | Launch your first run and understand the ports |
| [Interface](play/interface.md) | Learn the roster, city, activity panels, bubbles, and report view |
| [Agent Layouts](play/layouts.md) | Understand how 1-10+ agents are positioned |
| [Tool Hub](play/tool-hub.md) | Understand how tools are visualized |
| [Replay](play/replay.md) | Save and replay runs |
| [Command Reference](play/reference.md) | See CLI options and runtime capture details |
| [Troubleshooting](play/troubleshooting.md) | Fix START, stale UI, ports, blocked runs, and stopping |

## Mental Model

`lantern play` has three moving parts:

| Part | Role |
| --- | --- |
| Play server | Serves the UI and WebSocket event stream |
| Child process | Runs the target project from its own root |
| Browser UI | Displays agents, timeline, logs, tools, thoughts, and report output |

The UI does not auto-start by default. You start the run deliberately from the browser with **START**.

## Replay From The Same UI

`lantern replay` uses the same Play environment, but it replays a saved event stream instead of running the agent project again.

```bash
# First run and save a replay
lantern play /path/to/project --name demo-run

# Later, replay the saved run
lantern replay demo-run

# Or replay the newest saved run
lantern replay last
```

From inside the project root, this is enough:

```bash
lantern play
lantern replay demo-run
lantern replay last
```

When `lantern play` starts without `--name`, the UI asks for a run name before **START** and saves the replay with that name. `lantern replay` then opens the same pixel-art world with replay controls: pause, seek, speed, restart, and stop.

Use replay when you want to demo or debug a run without spending tokens or calling external tools again.

## Current Runtime Support

| Framework | Status |
| --- | --- |
| CrewAI | Live runtime instrumentation |
| Google ADK | Planned |
| LangGraph | Planned |
| AutoGen | Planned |
| Smolagents | Planned |

CrewAI is currently the primary supported runtime for live execution. Other frameworks can still be documented and detected by AgentLantern, but live Play instrumentation is not complete yet.
