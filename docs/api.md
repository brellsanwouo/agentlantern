# API Reference

## CLI Commands

Global options:

- `--help, -h` - Show help message
- `--version` - Show the installed AgentLantern version

### lantern docs

Generate documentation for an agent project.

```bash
lantern docs [PROJECT_PATH] [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH` (optional, default: current directory) - Path to the agent project

**Options:**
- `--help, -h` - Show help message
- `--no-generate` - Don't export diagrams (faster processing)

**Returns:**
- Generates documentation files in `PROJECT_PATH/docs/`
- Returns 0 on success, non-zero on error

**Example:**
```bash
lantern docs /home/user/my-project
lantern docs  # Uses current directory
```

### lantern web

Generate and serve an agent project's documentation over local HTTP.

```bash
lantern web [PROJECT_PATH] [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH` (optional, default: current directory) - Path to the agent project

**Options:**
- `--host HOST` (default: `0.0.0.0`) - Server host address
- `--port PORT` (default: `9000`) - Server port
- `--no-generate` - Don't regenerate documentation
- `--help, -h` - Show help message

**Returns:**
- Starts HTTP server and displays URL
- Use Ctrl+C to stop server

**Example:**
```bash
lantern web --port 9001
lantern web /path/to/project --host 0.0.0.0 --port 3000
```

### lantern play

Run a supported agent project and stream execution events to the animated Play UI.

```bash
lantern play [PROJECT_PATH] [OPTIONS]
```

**Arguments:**
- `PROJECT_PATH` (optional, default: current directory) - Path to the agent project

**Options:**
- `--ws-port PORT` (default: 7890) - WebSocket event stream port
- `--http-port PORT` (default: 7891) - HTTP UI port
- `--name NAME` - Save the run to `.lantern_replays/<name>.jsonl` and auto-start. If omitted, the UI asks for the run name before START
- `--help, -h` - Show help message

**Returns:**
- Starts the local Play UI
- Starts the crew only after the user enters or confirms a run name and clicks START, unless `--name` is provided
- Streams runtime events, logs, tool calls, delegation events, and final reports when available

**Example:**
```bash
lantern play /path/to/project
lantern play /path/to/project --ws-port 8790 --http-port 8791
lantern play /path/to/project --name demo-run
```

### lantern replay

Replay a saved Play run.

```bash
lantern replay NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Replay name from `.lantern_replays/<name>.jsonl` or a direct `.jsonl` path

**Options:**
- `--speed FLOAT` (default: 1.0) - Playback speed multiplier
- `--ws-port PORT` (default: 7890) - WebSocket event stream port
- `--http-port PORT` (default: 7891) - HTTP UI port
- `--help, -h` - Show help message

**Example:**
```bash
lantern replay demo-run
lantern replay demo-run --speed 2.0
lantern replay /path/to/.lantern_replays/demo-run.jsonl
```

## Generated Document Structure

### agents.md

Lists all agents with details:
- Agent name and role
- Responsibilities
- Available tools
- Assigned tasks

### tasks.md

Documents all tasks:
- Task name
- Description
- Assigned agent
- Output files
- Dependencies

### architecture.md

System architecture:
- High-level design overview
- Component relationships
- Data flow diagrams
- Technology stack

### diagrams.md

Visual representations:
- Task workflow diagrams
- Agent interaction diagrams
- Dependency graphs

### runbook.md

Execution documentation:
- Setup instructions
- How to run the crew
- Expected outputs
- Troubleshooting guide

### overview.md

Project summary:
- What the project does
- Key features
- Quick start guide
- Main components

### contact.md

Support information:
- Team contacts
- Support channels
- Contributing guidelines
- License information

## Configuration

AgentLantern uses your project's `pyproject.toml` and YAML configs:

```toml
[project]
name = "my-project"
version = "1.0.0"
description = "My CrewAI project"
```

Your YAML configs should be at:
- `src/[PROJECT_NAME]/config/agents.yaml`
- `src/[PROJECT_NAME]/config/tasks.yaml`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid project structure |
| 2 | Missing configuration files |
| 3 | Port already in use (web) |
| 4 | Parse error |

## File Output

Generated files include:
- Markdown (.md) - For version control and editing
- HTML (.html) - For web viewing
- Sidebar config (_sidebar.md) - Navigation

## Requirements

- Python 3.11+
- PyYAML 6.0.0+
- Valid supported agent project structure

## Error Messages

**"Could not find crew.py under [path]"**
- The CrewAI analyzer could not find the expected entrypoint
- Ensure CrewAI projects have `src/[name]/crew.py`

**"Address already in use"**
- Another service is using the port
- Use `--port [NUMBER]` to specify a different port

**"No such file or directory: config/agents.yaml"**
- Missing CrewAI configuration files
- Ensure CrewAI projects have `config/agents.yaml` and `config/tasks.yaml`
