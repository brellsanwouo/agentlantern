# lantern lint

`lantern lint` is AgentLantern's static checker for agent projects.

It catches design issues before runtime: missing agents, invalid task references, incomplete YAML fields, suspicious delegation settings, wrong field types, and other project structure problems.

It does not call an LLM and does not require network access.

## Pages

| Page | Use it for |
| --- | --- |
| [Run the Linter](lint/running.md) | Basic commands, strict mode, JSON mode |
| [CrewAI Rules](lint/rules.md) | Error, warning, and info rule reference |
| [JSON and CI](lint/json-ci.md) | Machine-readable output, exit codes, GitHub Actions, pre-commit |
| [Troubleshooting](lint/troubleshooting.md) | Common linter problems |

## How It Works

The linter reads the same project model that `lantern docs` uses:

- YAML config files,
- Python AST,
- framework-specific analyzer output.

Then it applies rules specific to the detected framework.

## Current Coverage

| Framework | Linter status |
| --- | --- |
| CrewAI | Full rule set |
| Google ADK | Planned |
| LangGraph | Planned |
| AutoGen | Planned |
| Smolagents | Planned |
