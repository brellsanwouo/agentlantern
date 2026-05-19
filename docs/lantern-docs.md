# lantern docs

`lantern docs` generates a complete, browsable documentation site from your agent project. It reads your code and configuration files statically — no LLM, no API keys.

## Usage

```bash
# From the project root
cd my-agent-project
lantern docs

# From anywhere
lantern docs /path/to/my-agent-project

# Custom output directory
lantern docs /path/to/my-agent-project -o /path/to/output

# Generate and serve immediately
lantern web
lantern web /path/to/my-agent-project --port 9000

# Serve without regenerating
lantern web --no-generate
```

## What Gets Generated

All files are written to `<project>/docs/` by default.

| File | Content |
|------|---------|
| `overview.md` | Project snapshot, entrypoints, high-level flow |
| `architecture.md` | System map, key files, dependencies, environment variables |
| `diagrams.md` | Mermaid diagrams — agent-task graph, execution flow, sequence |
| `agents.md` | Agent roles, goals, backstories, tools, LLM, delegation flags |
| `tasks.md` | Task descriptions, assigned agents, expected outputs, context |
| `runbook.md` | Install, configure, run, static checks, troubleshooting |
| `contact.md` | Project contacts from `pyproject.toml` |
| `index.html` | Docsify site — publishable to GitHub Pages |
| `_sidebar.md` | Navigation sidebar |
| `agentlantern-docs.html` | Self-contained shareable HTML bundle (single file, no server needed) |

## How It Works

1. **Detection** — AgentLantern scans `pyproject.toml` and the project structure to identify the framework
2. **Analysis** — the framework-specific analyzer parses agents, tasks, tools, LLM config, and env vars from code and YAML files (static AST parsing — no imports, no execution)
3. **Rendering** — a Markdown file is generated for each section, then assembled into a Docsify site

## Sharing Documentation

| Method | How |
|--------|-----|
| **Local** | `lantern web` → open `https://localhost:9000` |
| **Single file** | Send `docs/agentlantern-docs.html` — self-contained, works offline |
| **GitHub Pages** | Push `docs/` and enable Pages in repository settings |
| **Any web server** | `docs/` is a static site — works on Nginx, Vercel, Netlify |

## CI — Auto-generate on Push

```yaml
# .github/workflows/docs.yml
name: Generate Docs

on: [push]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
      - run: lantern docs
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/
```

## Quick Start (No API Keys Needed)

You can test `lantern docs` on a minimal CrewAI project without any LLM or API keys.

```bash
# 1. Create a scaffold project
pip install crewai
crewai create my_test_project
cd my_test_project

# 2. Generate documentation
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
lantern docs

# 3. Browse it
lantern web
# → https://localhost:9000
```

## Supported Frameworks

| Framework | Analysis level | What is extracted |
|-----------|---------------|-------------------|
| **CrewAI** | Full | Agents, tasks, tools, LLM, delegation, memory, Mermaid diagrams |
| **Google ADK** | Full | Agents, tools, workflows, Mermaid pipeline diagrams |
| **LangGraph** | Detected | Project metadata from `pyproject.toml` |
| **AutoGen** | Detected | Project metadata from `pyproject.toml` |
| **Smolagents** | Detected | Project metadata from `pyproject.toml` |
