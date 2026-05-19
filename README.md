# AgentLantern

**GitHub:** https://github.com/brellsanwouo/agentlantern

AgentLantern is a CLI devtool that automatically documents multi-agent LLM systems and lets you watch them run live.

Point it at an agent project — it detects the framework, parses the architecture, and generates a browsable documentation site. For supported frameworks it also opens a live animated playground while the crew executes.

## Install

**With pip:**
```bash
pip install agentlantern
```

**With uv (recommended — installs the `lantern` command globally):**
```bash
uv tool install agentlantern
```

**From source:**
```bash
git clone https://github.com/brellsanwouo/agentlantern
cd agentlantern
uv tool install -e .
# or: pip install -e .
```

Requires Python 3.11+.

## Quick Start

```bash
# Generate and browse documentation for your agent project (served over HTTPS)
lantern web path/to/your-project

# A self-signed certificate is generated once in ~/.agentlantern/ssl/ — accept the browser warning on first visit.

# Watch a CrewAI run live in the animated playground
lantern play path/to/your-project

# Generate docs only (written to <project>/docs/)
lantern docs path/to/your-project

# Lint the agent project for design issues
lantern lint path/to/your-project
```

## Commands

| Command | Description |
| --- | --- |
| `lantern docs [project] [-o DIR]` | Generate Markdown documentation |
| `lantern web [project] [--port PORT]` | Generate and serve project docs over HTTPS on `0.0.0.0:9000` by default |
| `lantern lint [project] [--strict] [--json]` | Static analysis — no LLM, no network |
| `lantern inspect [project]` | Output project model as JSON |
| `lantern play [project] [--name NAME]` | Live animated playground; if `--name` is omitted, the UI asks for a run name |
| `lantern replay NAME [--speed N]` | Replay a saved run |

## Supported Frameworks

| Framework | Status |
| --- | --- |
| **CrewAI** | Full analysis and live playground |
| **LangGraph** | Detected — analysis coming soon |
| **AutoGen** | Detected — analysis coming soon |
| **Smolagents** | Detected — analysis coming soon |
| **Google ADK** | Detected — analysis coming soon |

Detection is automatic — no configuration needed.

## What Gets Generated

`lantern docs` writes these files into `<project>/docs/`:

| File | Content |
| --- | --- |
| `overview.md` | Project snapshot, entrypoints, high-level flow |
| `architecture.md` | System map, key files, dependencies, env vars |
| `agents.md` | Agent roles, goals, tools, backstories |
| `tasks.md` | Task descriptions, agents, expected outputs |
| `diagrams.md` | Mermaid diagrams: agent-task graph, execution flow, sequence |
| `runbook.md` | Install, configure, run, static checks, troubleshooting |
| `contact.md` | Project contacts from `pyproject.toml` |
| `index.html` | Docsify site (publishable to GitHub Pages) |
| `agentlantern-docs.html` | Self-contained shareable HTML bundle |

## Play UI

`lantern play` opens a pixel-art playground that visualizes a supported agent run:

- **START / STOP / RESTART** controls
- Run name field in the UI when `--name` is not provided
- Up to 10 agents, each in their own named zone on the map
- A central **Tool Hub** agents visually consult when tools are used
- Timeline, Thoughts, Tools, Comms, and Log panels
- Clickable agents with full per-agent history
- Final report display on completion
- **Replay** — save a run with `--name my-run` and replay it anytime with `lantern replay my-run`

## Linter

`lantern lint` analyzes your project statically:

```
AgentLantern Lint — my-crew (CrewAI)

  ✗  [E002]  crew.py:18   Task `analyze` references agent `researcher` which is not declared in agents.yaml.
  △  [W006]  agents.yaml:4   Agent `writer` is missing required field `backstory`.
  ·  [I001]  No tool detected — may be intentional for a pure LLM workflow.

  Summary: 1 error, 1 warning, 1 info
```

Rules: **E001–E002** (errors), **W001–W008** (warnings), **I001–I004** (info).

## Contributing

```
src/agentlantern/
├── core/            # BaseProject, BaseAnalyzer, BaseRenderer
├── frameworks/
│   ├── registry.py  # auto-detection
│   ├── crewai/      # full analyzer + renderer
│   ├── langgraph/   # stub
│   ├── autogen/     # stub
│   ├── smolagents/  # stub
│   └── google_adk/  # stub
├── docs.py          # doc orchestrator
├── play.py          # live playground server
└── cli.py
```

To add a new framework: create `src/agentlantern/frameworks/<name>/analyzer.py` implementing `detect`, `analyze`, `get_renderer`, then register it in `registry.py`.

## License

MIT — see [LICENSE](LICENSE)
