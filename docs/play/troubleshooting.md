# Play Troubleshooting

## START Does Nothing

Check that the browser is connected to the right WebSocket port.

For custom ports:

```bash
lantern play --ws-port 8790 --http-port 8791
```

open:

```text
http://127.0.0.1:8791?ws=8790
```

The UI also infers `ws = http_port - 1`, so `http://127.0.0.1:8791` should connect to `8790`.

## UI Is Stale After Updating AgentLantern

An already-open tab can keep old JavaScript in memory. Close the tab and reopen the printed URL.

If installed with `uv tool`:

```bash
uv tool install agentlantern --force
```

When developing from a local checkout:

```bash
uv tool install --force --refresh .
```

## Port Already in Use

Use another HTTP/WebSocket pair:

```bash
lantern play --ws-port 8792 --http-port 8793
```

## Run Starts but Agents Do Not Move

The target project may be blocked by:

- missing API keys,
- long model calls,
- dependency installation,
- a tool call,
- project startup errors.

Check the **Log** panel and the terminal running `lantern play`.

## Stop a Run

Use **STOP** in the UI first.

If the process does not exit, press `Ctrl+C` in the terminal running `lantern play`.
