from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentlantern import __version__
from agentlantern.docs import generate_docs
from agentlantern.inspect import run_inspect
from agentlantern.lint import run_lint
from agentlantern.web import serve_docs


def _latest_replay_path(replays_dir: Path = Path(".lantern_replays")) -> Path:
    """Return the newest replay in the current project's replay directory."""
    replays = [
        path
        for path in replays_dir.glob("*.jsonl")
        if path.is_file()
    ]
    if not replays:
        print(f"\n  Error: no saved replay found in {replays_dir}/")
        print("  Run 'lantern play' first, enter a replay name, then click START.")
        print()
        sys.exit(1)
    return max(replays, key=lambda path: (path.stat().st_mtime, path.name))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lantern",
        description=(
            "AgentLantern — a suite of tools for multi-agent LLM systems. "
            "Run from the root of an agent project."
        ),
        epilog="Example: cd my-crew-project && lantern docs",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── docs ──────────────────────────────────────────────────────────────────
    docs_parser = subparsers.add_parser(
        "docs",
        help="Generate Markdown documentation for an agent project.",
    )
    docs_parser.add_argument(
        "project", nargs="?", default=".",
        help="Path to the agent project to document.",
    )
    docs_parser.add_argument(
        "-o", "--output-dir", default=None,
        help="Directory where documentation should be written. Defaults to <project>/docs.",
    )

    # ── lint ──────────────────────────────────────────────────────────────────
    lint_parser = subparsers.add_parser(
        "lint",
        help="Lint an agent project and report design issues.",
    )
    lint_parser.add_argument(
        "project", nargs="?", default=".",
        help="Path to the agent project to lint.",
    )
    lint_parser.add_argument(
        "--strict", action="store_true",
        help="Exit with code 1 if any warning or info finding is present (not just errors).",
    )
    lint_parser.add_argument(
        "--json", action="store_true",
        help="Output findings as JSON (for tooling integration).",
    )

    # ── inspect ───────────────────────────────────────────────────────────────
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Output project structure as JSON (for tooling/IDE integration).",
    )
    inspect_parser.add_argument(
        "project", nargs="?", default=".",
        help="Path to the agent project to inspect.",
    )

    # ── web ───────────────────────────────────────────────────────────────────
    web_parser = subparsers.add_parser(
        "web",
        help="Serve generated AgentLantern docs in a local web app.",
    )
    web_parser.add_argument(
        "project", nargs="?", default=".",
        help="Path to the agent project whose docs should be served.",
    )
    web_parser.add_argument("--host", default="0.0.0.0")
    web_parser.add_argument("--port", type=int, default=9000)
    web_parser.add_argument(
        "--no-generate", action="store_true",
        help="Do not regenerate docs before serving.",
    )

    # ── play ──────────────────────────────────────────────────────────────────
    play_parser = subparsers.add_parser(
        "play",
        help="Watch your agents run — live animated visualization of crew execution.",
    )
    play_parser.add_argument(
        "project", nargs="?", default=".",
        help="Path to the agent project to run and visualize.",
    )
    play_parser.add_argument(
        "--ws-port", type=int, default=7890,
        help="WebSocket port for event streaming (default: 7890).",
    )
    play_parser.add_argument(
        "--http-port", type=int, default=7891,
        help="HTTP port for the Play UI (default: 7891).",
    )
    play_parser.add_argument(
        "--name", default="",
        help=(
            "Replay name for this run. When omitted, the Play UI asks for one "
            "before START."
        ),
    )

    # ── replay ────────────────────────────────────────────────────────────────
    replay_parser = subparsers.add_parser(
        "replay",
        help="Replay a saved crew run in the animated UI.",
    )
    replay_parser.add_argument(
        "name",
        help=(
            "Replay name (looks for .lantern_replays/<name>.jsonl in cwd) "
            "or a direct path to a .jsonl file. Use 'last' to replay the "
            "newest saved run."
        ),
    )
    replay_parser.add_argument(
        "--speed", type=float, default=1.0,
        help="Playback speed multiplier (default: 1.0, use 2.0 for double speed).",
    )
    replay_parser.add_argument(
        "--ws-port", type=int, default=7890,
        help="WebSocket port for event streaming (default: 7890).",
    )
    replay_parser.add_argument(
        "--http-port", type=int, default=7891,
        help="HTTP port for the Play UI (default: 7891).",
    )

    return parser


def main() -> None:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.command == "docs":
        output_dir = Path(args.output_dir) if args.output_dir else None
        result = generate_docs(Path(args.project), output_dir=output_dir)
        print(f"Generated AgentLantern docs for {result.project_name} ({result.framework})")
        for file_path in result.files:
            print(f"- {file_path}")

    elif args.command == "lint":
        run_lint(Path(args.project), strict=args.strict, as_json=args.json)

    elif args.command == "inspect":
        run_inspect(Path(args.project))

    elif args.command == "web":
        serve_docs(
            Path(args.project),
            host=args.host,
            port=args.port,
            generate=not args.no_generate,
        )

    elif args.command == "play":
        from agentlantern.play import run_play
        run_play(
            Path(args.project),
            ws_port=args.ws_port,
            http_port=args.http_port,
            name=args.name,
        )

    elif args.command == "replay":
        from agentlantern.play import run_replay
        name = args.name
        if name == "last":
            replay_path = _latest_replay_path()
            print(f"Replaying latest saved run: {replay_path}")
        else:
            replay_path = Path(name)
        if name != "last" and not replay_path.exists():
            # Look for it in .lantern_replays/<name>.jsonl relative to cwd
            candidate = Path(".lantern_replays") / f"{name}.jsonl"
            if not candidate.exists():
                # Also try with .jsonl already in name
                candidate2 = Path(".lantern_replays") / name
                candidate = candidate2 if candidate2.exists() else candidate
            replay_path = candidate
        run_replay(
            replay_path,
            speed=args.speed,
            ws_port=args.ws_port,
            http_port=args.http_port,
        )
