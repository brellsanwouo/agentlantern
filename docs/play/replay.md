# Replay

Replay mode lets you save a run and inspect it later without re-running the crew.

## Save a Run

```bash
lantern play /path/to/project --name demo-run
```

This writes:

```text
.lantern_replays/demo-run.jsonl
```

Named runs auto-start. The start overlay is skipped.

If you start Play without `--name`, the UI asks for a run name before START and uses that name for the saved replay.

## Replay by Name

From the same project root:

```bash
lantern replay demo-run
```

## Replay by Path

```bash
lantern replay /path/to/.lantern_replays/demo-run.jsonl
```

## Playback Speed

```bash
lantern replay demo-run --speed 2.0
```

## UI Controls

Replay mode adds controls for:

- pause/resume,
- speed,
- seek,
- restart,
- stop.

## When to Use Replay

Replay is useful for:

- demos,
- debugging a run after it finished,
- comparing UI behavior without spending tokens again,
- sharing a deterministic reproduction with another developer.
