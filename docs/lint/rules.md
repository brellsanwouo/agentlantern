# CrewAI Lint Rules

Rules are grouped by severity. Codes are stable across versions.

## Errors

Errors indicate broken project structure and should be fixed before running or documenting the project.

| Code | Rule | What it checks |
| --- | --- | --- |
| E001 | Task has no agent | A task in `tasks.yaml` has no `agent` field |
| E002 | Agent not declared | A task references an agent name that does not exist in `agents.yaml` |

## Warnings

Warnings identify likely design issues.

| Code | Rule | What it checks |
| --- | --- | --- |
| W001 | Idle agent | An agent is declared in `agents.yaml` but no task is assigned to it |
| W002 | Useless delegation | `allow_delegation=True` on the only agent in the crew |
| W003 | No expected output | A task has no `expected_output` |
| W004 | No pyproject.toml | Project metadata is missing |
| W005 | Vague role | Agent `role` is fewer than 5 characters |
| W006 | Missing required field | Required YAML field is empty or absent |
| W007 | Unknown field | Field is not part of the CrewAI schema |
| W008 | Wrong type | Field value has the wrong type |

## Info

Info findings are optional improvements.

| Code | Rule | What it checks |
| --- | --- | --- |
| I001 | No tools | No tool is used anywhere in the crew |
| I002 | Template placeholders | `pyproject.toml` still contains scaffold defaults |
| I003 | Very long goal | Agent `goal` exceeds 500 characters |
| I004 | Very long task description | Task `description` exceeds 800 characters |

## Agent Field Schema

The linter validates against the CrewAI agent schema:

| Field | Type | Required |
| --- | --- | --- |
| `role` | string | yes |
| `goal` | string | yes |
| `backstory` | string | yes |
| `llm` | string or dict | no |
| `tools` | list | no |
| `max_iter` | int | no |
| `max_rpm` | int | no |
| `max_execution_time` | int or float | no |
| `memory` | bool | no |
| `verbose` | bool | no |
| `allow_delegation` | bool | no |
| `cache` | bool | no |
| `allow_code_execution` | bool | no |
| `max_retry_limit` | int | no |
| `knowledge_sources` | list | no |
| `embedder` | dict | no |
| `use_system_prompt` | bool | no |
| `respect_context_window` | bool | no |

## Task Field Schema

| Field | Type | Required |
| --- | --- | --- |
| `description` | string | yes |
| `expected_output` | string | yes |
| `agent` | string or dict | no |
| `tools` | list | no |
| `context` | list | no |
| `async_execution` | bool | no |
| `human_input` | bool | no |
| `output_file` | string | no |
| `output_json` | dict | no |
| `output_pydantic` | dict | no |
| `callback` | dict | no |
