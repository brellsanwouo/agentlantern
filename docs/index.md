---
layout: home

hero:
  name: AgentLantern
  text: Developer tools for AI agent projects
  tagline: Generate clean architecture docs, lint agent design, inspect project structure, and watch supported agent runs in a live animated playground.
  image:
    src: ./assets/logo.png
    alt: AgentLantern logo
  actions:
    - theme: brand
      text: Get Started
      link: /installation
    - theme: alt
      text: CLI Guide
      link: /usage
    - theme: alt
      text: lantern play
      link: /play

features:
  - title: Document agent systems
    details: Generate a browsable docs site with overview, architecture, diagrams, agents, tasks, runbook, and contacts.
  - title: Lint before runtime
    details: Catch missing fields, broken references, idle agents, risky config, and CI-facing issues without calling an LLM.
  - title: Watch runs live
    details: Start, stop, replay, and inspect supported agent runs inside a pixel-art execution environment.
---

<div class="agentlantern-hero-mark">
  <img src="./assets/logo-horizontal.png" alt="AgentLantern" />
</div>

<div class="agentlantern-pill-row">
  <span class="agentlantern-pill">Multi-framework direction</span>
  <span class="agentlantern-pill">CrewAI deep support today</span>
  <span class="agentlantern-pill">GitHub Pages ready</span>
</div>

<div class="agentlantern-command-grid">
  <div class="agentlantern-command">
    <strong>lantern docs</strong>
    <span>Generate Markdown and a static docs site from an agent project.</span>
  </div>
  <div class="agentlantern-command">
    <strong>lantern lint</strong>
    <span>Run deterministic project checks locally or in CI.</span>
  </div>
  <div class="agentlantern-command">
    <strong>lantern play</strong>
    <span>Open the animated UI, name the run, then start and inspect execution.</span>
  </div>
</div>

## Fast Start

```bash
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or
uv tool install git+https://github.com/brellsanwouo/agentlantern.git
```

```bash
lantern web /path/to/my-agent-project
lantern lint /path/to/my-agent-project
lantern play /path/to/my-agent-project
```
