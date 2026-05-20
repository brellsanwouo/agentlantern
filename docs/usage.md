# Usage Guide

## Commands

### `lantern lint [project] [--strict] [--json]`

Analyzes an agent project for design issues without using an LLM.

```bash
# From the project root
cd my-agent-project
lantern lint

# From anywhere
lantern lint /path/to/my-agent-project

# Exit with code 1 on any finding (CI-friendly)
lantern lint --strict

# Machine-readable output for CI pipelines and integrations
lantern lint --json
```

See the [Linter reference](linter.md) for all rules and codes.

### `lantern inspect [project]`

Outputs the full project model as JSON for integrations and debugging.

```bash
lantern inspect /path/to/my-agent-project
```

### `lantern play [project] [--ws-port PORT] [--http-port PORT] [--name NAME]`

Runs a supported agent project and opens the live animated Play UI.

```bash
# From the project root
cd my-agent-project
lantern play

# From anywhere
lantern play /path/to/my-agent-project

# Custom ports
lantern play /path/to/my-agent-project --ws-port 8790 --http-port 8791

# Save the run for replay and auto-start it
lantern play /path/to/my-agent-project --name demo-run
```

The browser UI starts in a ready state. If `--name` is omitted, the UI asks for a run name before **START**. Use **STOP** to terminate the active run.

The Play UI includes dynamic 1-10 agent layouts, a central Tool Hub for tool calls, timeline/thoughts/tools/comms/log panels, clickable agent history, and final `report.md` display when available.

See the [Play reference](play.md).

### `lantern replay NAME [--speed FLOAT]`

Replays a saved `lantern play --name` run.

```bash
lantern replay demo-run
lantern replay demo-run --speed 2.0
lantern replay /path/to/.lantern_replays/demo-run.jsonl
```

### `lantern docs [project] [-o OUTPUT_DIR]`

Generates documentation for an agent project.

```bash
# From the project root
cd my-agent-project
lantern docs

# From anywhere
lantern docs /path/to/my-agent-project

# Custom output directory
lantern docs /path/to/my-agent-project -o /path/to/output
```

### `lantern web [project]`

Generates (unless `--no-generate`) and serves the documentation for an agent project over local HTTP.

```bash
# From the project root
cd my-agent-project
lantern web

# From anywhere
lantern web /path/to/my-agent-project

# Custom port
lantern web --port 9000

# Serve without regenerating
lantern web --no-generate

# Accessible on the local network
lantern web --host 0.0.0.0
```

By default, `lantern web` serves `http://localhost:9000` over local HTTP, so the browser should not show a certificate warning.

## Supported Frameworks

AgentLantern detects the framework automatically from `pyproject.toml` dependencies or project structure.

| Framework | Detection signal | Analysis level |
| --- | --- | --- |
| **CrewAI** | `crewai` dep or `crew.py` + `@CrewBase` | Full — agents, tasks, diagrams, env vars |
| **LangGraph** | `langgraph` dep | Detected — basic info from `pyproject.toml` |
| **AutoGen** | `autogen-agentchat` or `pyautogen` dep | Detected — basic info from `pyproject.toml` |
| **Smolagents** | `smolagents` dep | Detected — basic info from `pyproject.toml` |
| **Google ADK** | `google-adk` dep | Detected — basic info from `pyproject.toml` |

For frameworks with full analysis, AgentLantern parses agents, tasks, tools, environment variables, and generates Mermaid diagrams.

For frameworks detected but not yet fully analyzed, AgentLantern generates a documentation site with the project metadata available and indicates that deeper analysis is coming.

## Generated Files

| File | Content |
| --- | --- |
| `overview.md` | Project snapshot, entrypoints, high-level flow |
| `architecture.md` | System map, key files, dependencies, environment variables |
| `diagrams.md` | Mermaid diagrams: agent-task graph, execution flow, sequence |
| `agents.md` | Agent roles, goals, tools, backstories |
| `tasks.md` | Task descriptions, agents assigned, expected outputs |
| `runbook.md` | Install, configure, run, static checks, troubleshooting |
| `contact.md` | Project contacts from `pyproject.toml` |
| `index.html` | Docsify site — publishable to GitHub Pages |
| `_sidebar.md` | Navigation menu |
| `agentlantern-docs.html` | Self-contained shareable HTML bundle |

## Typical Workflow

```bash
# 1. Navigate to (or point at) your agent project
cd my-agent-project

# 2. Generate and view documentation
lantern web

# 3. Open http://localhost:9000
# 4. Press Ctrl+C to stop the server
```

## Multiple Projects

```bash
# Terminal 1
lantern web ~/projects/crew-project --port 9000

# Terminal 2
lantern web ~/projects/adk-project --port 9001
```

## Sharing Documentation

The generated `docs/` folder is a static site. To share it:

- **GitHub Pages** — push `docs/` and enable GitHub Pages in repository settings
- **Single-file share** — send `docs/agentlantern-docs.html` (self-contained, no server needed)
- **Any web server** — `docs/` works on Nginx, Vercel, Netlify, etc.

## Next Steps

- [Examples](examples.md)
- [FAQ](faq.md)
