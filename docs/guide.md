# AgentLantern

**AgentLantern is a suite of developer tools for multi-agent LLM systems.**

Point it at any agent project — it detects the framework automatically, documents the architecture, checks design issues, and can visualize supported crews while they run.

---

## Lantern Tools

AgentLantern is organized around a small CLI surface. Each command does one job and can be used from the root of an agent project or with an explicit project path.

<div class="tool-stack">
  <a class="tool-row" href="./lantern-docs">
    <div class="tool-index">01</div>
    <div class="tool-copy">
      <h3>Document the system</h3>
      <p>Generate a structured docs site with overview, architecture, diagrams, agents, tasks, runbook, and contacts.</p>
    </div>
    <code>lantern web</code>
  </a>
  <a class="tool-row" href="./linter">
    <div class="tool-index">02</div>
    <div class="tool-copy">
      <h3>Check the design</h3>
      <p>Run deterministic lint rules for missing fields, broken references, idle agents, YAML issues, and CI output.</p>
    </div>
    <code>lantern lint</code>
  </a>
  <a class="tool-row" href="./play">
    <div class="tool-index">03</div>
    <div class="tool-copy">
      <h3>Watch the run</h3>
      <p>Start, stop, inspect, and replay supported agent runs inside the animated Play environment.</p>
    </div>
    <code>lantern play</code>
  </a>
</div>

```bash
lantern web      # generate and serve docs for the current project
lantern lint     # inspect project quality without LLM calls
lantern play     # open the live animated run viewer
```

---

## Supported Frameworks

| Framework | `lantern docs` | `lantern lint` | `lantern play` |
|-----------|:--------------:|:--------------:|:--------------:|
| **CrewAI** | ✅ Full analysis | ✅ 13 rules | ✅ Live runtime |
| **Google ADK** | ✅ Full analysis | Planned | Planned |
| **LangGraph** | Detected | Planned | Planned |
| **AutoGen** | Detected | Planned | Planned |
| **Smolagents** | Detected | Planned | Planned |

Framework detection is automatic — no configuration needed.

---

## Installation

```bash
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or (recommended)
uv tool install git+https://github.com/brellsanwouo/agentlantern.git
```

Verify:

```bash
lantern --help
```

See the full [Installation guide](installation.md).
