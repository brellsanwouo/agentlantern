# Lint Troubleshooting

## No Framework Detected

Check that `pyproject.toml` lists a supported framework dependency.

For CrewAI, AgentLantern can also detect `crew.py` with `@CrewBase`.

## Missing CrewAI Config

For CrewAI projects, verify that these files exist and are populated:

```text
src/<project_name>/crew.py
src/<project_name>/config/agents.yaml
src/<project_name>/config/tasks.yaml
```

## Unexpected Unknown Field Warning

Unknown fields may be:

- a typo,
- an unsupported CrewAI version feature,
- an intentional custom extension.

If intentional, treat the warning as informational until AgentLantern supports that field.

## Strict Mode Fails CI

`--strict` fails on warnings and info findings.

Start with:

```bash
lantern lint --json
```

Then move to:

```bash
lantern lint --json --strict
```

once the project is clean enough for stricter enforcement.
