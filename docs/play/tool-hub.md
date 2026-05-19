# Tool Hub

The Tool Hub is the central object in the Play city.

It represents shared capabilities such as search, code execution, APIs, file access, data stores, and custom CrewAI tools.

## Why It Exists

Tool usage should not be hidden in stdout. In multi-agent systems, tools are often where the important external work happens.

The Tool Hub makes this visible.

## Visual Behavior

| Event | Visual behavior |
| --- | --- |
| Task starts | Tool Hub sends a check-in signal to the active agent |
| Tool call occurs | Agent visually consults the Tool Hub |
| Tool is detected | Tool station appears around the Tool Hub |
| Tool call is logged | Entry appears in Tools and Timeline |

## Tools Panel

The **Tools** panel shows:

- tool name,
- calling agent,
- input snippet,
- timestamp.

The same event is also added to the timeline.

## CrewAI Tool Capture

For CrewAI, AgentLantern captures generic tool calls by instrumenting `BaseTool.run` inside the child process.

It also captures delegation-style tools separately when CrewAI exposes them:

- coworker questions,
- delegated work,
- tool call results when available.

## Limitation

Tool capture depends on the framework runtime. If a tool is called outside the supported hooks or in a separate process not controlled by the run, it may only appear in raw stdout.
