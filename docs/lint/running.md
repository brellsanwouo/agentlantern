# Run the Linter

## Basic Usage

From the project root:

```bash
lantern lint
```

From anywhere:

```bash
lantern lint /path/to/my-agent-project
```

## Strict Mode

By default, only errors fail the process.

Use `--strict` to fail on any finding, including warnings and info:

```bash
lantern lint --strict
```

This is useful in CI when you want a clean project model.

## JSON Output

Use `--json` for machines:

```bash
lantern lint --json
```

Use both flags in CI:

```bash
lantern lint --json --strict
```

## Typical Workflow

1. Run `lantern lint`.
2. Fix errors first.
3. Review warnings next.
4. Decide whether info findings are intentional.
5. Add `--strict` in CI once the project is stable.
