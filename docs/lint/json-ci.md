# JSON and CI

## JSON Output

```bash
lantern lint --json
```

Example:

```json
{
  "project": "my-crew",
  "framework": "CrewAI",
  "root": "/path/to/project",
  "findings": [
    {
      "severity": "error",
      "code": "E001",
      "message": "Task `analyze` has no declared agent.",
      "location": "task `analyze`",
      "file": "src/my_crew/config/tasks.yaml",
      "line": 12
    }
  ]
}
```

`file` and `line` are `null` when a finding cannot be pinned to a specific source location.

## Exit Codes

| Exit code | Meaning |
| --- | --- |
| 0 | No issues, or only warnings/info in default mode |
| 1 | At least one error, or any finding with `--strict` |

## GitHub Actions

```yaml
- name: AgentLantern lint
  run: |
    pip install agentlantern
    lantern lint --json --strict my-agent-project/ | tee lint-results.json
```

## Pre-commit Hook

```yaml
repos:
  - repo: local
    hooks:
      - id: agentlantern-lint
        name: AgentLantern lint
        entry: lantern lint --strict
        language: system
        pass_filenames: false
```
