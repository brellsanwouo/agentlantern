# Installation

## Requirements

- Python 3.11 or higher

## Install

```bash
pip install "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
```

Or with `uv` (recommended):

```bash
uv tool install git+https://github.com/brellsanwouo/agentlantern.git
```

## Verify

```bash
lantern --help
lantern --version
```

## Supported Frameworks

AgentLantern automatically detects the framework — no extra dependencies to install.

| Framework | Detection |
| --- | --- |
| **CrewAI** | `crewai` in project dependencies |
| **LangGraph** | `langgraph` in project dependencies |
| **AutoGen** | `autogen-agentchat` or `pyautogen` in project dependencies |
| **Smolagents** | `smolagents` in project dependencies |
| **Google ADK** | `google-adk` in project dependencies |

## Update

```bash
pip install --upgrade "agentlantern @ git+https://github.com/brellsanwouo/agentlantern.git"
# or
uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git
```

## Uninstall

```bash
pip uninstall agentlantern
# or
uv tool uninstall agentlantern
```

## Troubleshooting

### `lantern: command not found`

For `uv tool` installs, ensure `~/.local/bin` is in your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Wrong version in PATH

```bash
which lantern   # should point to ~/.local/bin/lantern
uv tool install --force git+https://github.com/brellsanwouo/agentlantern.git
```

## Next Steps

- [Usage guide](usage.md)
- [Examples](examples.md)
