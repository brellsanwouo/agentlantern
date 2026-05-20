# Play Command Reference

## `lantern play`

```bash
lantern play [project] [--ws-port PORT] [--http-port PORT] [--name NAME]
```

| Option | Default | Description |
| --- | --- | --- |
| `project` | current directory | Agent project to run |
| `--ws-port` | `7890` | WebSocket port for live events |
| `--http-port` | `7891` | HTTP port for the Play UI |
| `--name` | empty | Save the run as `.lantern_replays/<name>.jsonl` and auto-start. If omitted, the UI asks for the run name before START |

## `lantern replay`

```bash
lantern replay NAME [--speed FLOAT] [--ws-port PORT] [--http-port PORT]
```

| Option | Default | Description |
| --- | --- | --- |
| `NAME` | required | Replay name or direct `.jsonl` path |
| `--speed` | `1.0` | Playback speed multiplier |
| `--ws-port` | `7890` | WebSocket port for replay events |
| `--http-port` | `7891` | HTTP port for the replay UI |

## CrewAI Runtime Events

CrewAI is the primary supported runtime for `lantern play`.

AgentLantern instruments the child process and captures:

| Event type | Description |
| --- | --- |
| Crew lifecycle | crew start, crew done, process messages |
| Tasks | task start, task done, task error |
| Thoughts | agent step or callback output when available |
| Delegation | coworker questions and delegated work |
| Tools | generic CrewAI `BaseTool.run` calls |
| stdout | raw terminal output from the child process |

For a standard CrewAI scaffold, the target command is usually:

```bash
uv run run_crew
```

AgentLantern detects and runs the appropriate command from the project root.
