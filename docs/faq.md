# FAQ

## Frameworks & Detection

### Which frameworks does AgentLantern support?

| Framework | Analysis | Detection |
| --- | --- | --- |
| **CrewAI** | Full | `crewai` in dependencies, or `crew.py` with `@CrewBase` |
| **LangGraph** | Coming soon | `langgraph` in dependencies |
| **AutoGen** | Coming soon | `autogen-agentchat` or `pyautogen` in dependencies |
| **Smolagents** | Coming soon | `smolagents` in dependencies |
| **Google ADK** | Coming soon | `google-adk` in dependencies |

### What happens if my framework is not yet fully supported?

AgentLantern still generates a documentation site. It reads `pyproject.toml` (project name, version, contacts, dependencies) and produces all the standard pages with a notice that detailed analysis for this framework is coming.

### How does auto-detection work?

AgentLantern reads `pyproject.toml` and looks for known framework names in the `dependencies` list. For CrewAI it also looks for `crew.py` with a `@CrewBase` decorator as a fallback.

### What if no framework is detected?

You will see a `NoFrameworkDetected` error listing the supported frameworks. Make sure your `pyproject.toml` includes the framework as a dependency.

### Can I use AgentLantern with a custom / internal agent framework?

Yes — add a new analyzer in `src/agentlantern/frameworks/<name>/analyzer.py` and register it in `src/agentlantern/frameworks/registry.py`. See the [README](https://github.com/brellsanwouo/AgentLantern) for details.

## Installation

### What Python versions are required?

Python 3.11 or higher.

### How do I install AgentLantern?

```bash
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or
uv tool install git+https://github.com/brellsanwouo/agentlantern.git
```

### How do I update?

```bash
pip install --upgrade "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or
uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git
```

### `lantern` command not found after install

If installed with `uv tool`, make sure `~/.local/bin` is in your `PATH`. Check with:

```bash
uv tool list
which lantern
```

### Which `lantern` is being used?

```bash
which lantern
```

If it points to an old version (e.g. `~/.local/share/uv/tools/agentlantern/`), reinstall:

```bash
uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git
```

## Usage

### How do I generate documentation?

```bash
lantern docs /path/to/your-agent-project
# or from the project root:
lantern docs
```

### How do I view the documentation?

```bash
lantern web /path/to/your-agent-project
# Open https://localhost:9000
```

To preview AgentLantern's own documentation site from this repository, do not use `lantern web .`. Use:

```bash
npm install
npm run docs:dev
```

### How do I watch a crew run live?

Use `lantern play`:

```bash
lantern play /path/to/your-agent-project
```

Open the URL printed in the terminal, then click **START** in the UI. Use **STOP** to terminate the active run.

If you did not pass `--name`, the UI asks for a run name before START and saves the replay with that name.

### What does `lantern play` show?

It shows a pixel-art live playground with dynamic agent placement, agent thought bubbles, a central Tool Hub for tool calls, timeline/thoughts/tools/comms/log panels, and final `report.md` display when available.

For 1 to 10 agents, the UI uses dedicated layouts with exactly `n` visible agents. No empty agent placeholders are displayed.

### Port 9000 is already in use

```bash
lantern web --port 9001
```

### How do I stop the web server?

Press `Ctrl+C` in the terminal running `lantern web`.

### Can I serve without regenerating?

```bash
lantern web --no-generate
```

### Can I run documentation for multiple projects at the same time?

Yes — use a different port for each:

```bash
lantern web ~/projects/project-a --port 9000
lantern web ~/projects/project-b --port 9001
```

## Documentation Content

### Can I edit the generated files?

Yes, but they will be overwritten the next time you run `lantern docs`.

### How do I share the documentation without running a server?

Send `docs/agentlantern-docs.html` — it is a self-contained HTML file that works without any server.

### How do I publish to GitHub Pages?

1. Run `lantern docs`
2. Commit and push the `docs/` folder
3. Enable GitHub Pages in repository settings, source: `/docs`

### Why don't the Mermaid diagrams render?

Mermaid requires a browser environment. Use `lantern web` (or any web viewer that supports Mermaid) instead of a plain Markdown editor.

## Troubleshooting

### `NoFrameworkDetected` error

Check that `pyproject.toml` lists a supported framework in `[project] dependencies`.

### `FileNotFoundError: Could not find crew.py`

You are running an old version of `lantern`. Update with `uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git`.

### Documentation content is empty

For CrewAI: verify that `agents.yaml`, `tasks.yaml`, and `crew.py` exist and are populated, then re-run `lantern docs`.

### `lantern play` opens, but START does nothing

First confirm the browser is connected to the WebSocket port printed by `lantern play`. With custom ports:

```bash
lantern play --ws-port 8790 --http-port 8791
```

open:

```text
http://127.0.0.1:8791?ws=8790
```

If the UI still appears stale, close the tab and reopen the printed URL. If installed with `uv tool`, refresh the command:

```bash
uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git
```

When developing AgentLantern from a local checkout:

```bash
uv tool install --force --refresh .
```

### `lantern play` starts, but the UI does not update

Check the **Log** panel and the terminal running `lantern play`. The target project may be waiting on an API key, model call, dependency install, or external tool. For browser cache issues, close the old tab and reopen the printed URL.

### How do I save and replay a run?

```bash
lantern play /path/to/project --name demo-run
lantern replay demo-run
```

Saved runs are written to `.lantern_replays/<name>.jsonl` in the target project.

## General

### Is AgentLantern free?

Yes — MIT license, open source.

### Where do I report bugs?

Open an issue on the [GitHub repository](https://github.com/brellsanwouo/AgentLantern).

### Can I contribute?

Yes — contributions are welcome, especially new framework analyzers.
