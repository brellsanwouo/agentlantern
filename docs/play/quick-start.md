# Play Quick Start

## Start the Play UI

From the root of an agent project:

```bash
lantern play
```

From anywhere:

```bash
lantern play /path/to/my-agent-project
```

AgentLantern prints two local endpoints:

| Service | Default | Purpose |
| --- | --- | --- |
| HTTP UI | `http://127.0.0.1:7891` | Browser interface |
| WebSocket | `ws://127.0.0.1:7890` | Live event stream |

Open the printed HTTP URL.

## Run the Crew

1. Wait for the UI status to show **Ready**.
2. Click **START**.
3. Watch the city, timeline, tools, comms, and log panels.
4. Click **STOP** if the run is too long or blocked.
5. Click **RESTART** to launch a fresh run.

The crew does not start automatically unless you pass `--name`. Without `--name`, the UI asks for a run name before START.

## Custom Ports

Use custom ports when defaults are already taken:

```bash
lantern play /path/to/project --ws-port 8790 --http-port 8791
```

Open:

```text
http://127.0.0.1:8791?ws=8790
```

The UI also infers the WebSocket port from the HTTP port (`8791` -> `8790`) when `?ws=` is missing.

## Save a Run While Starting

```bash
lantern play /path/to/project --name demo-run
```

This saves events to:

```text
.lantern_replays/demo-run.jsonl
```

It also skips the start overlay and launches automatically.
