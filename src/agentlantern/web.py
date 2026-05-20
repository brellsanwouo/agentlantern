from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agentlantern.docs import generate_docs


def serve_docs(
    project_root: Path,
    *,
    host: str = "0.0.0.0",
    port: int = 9000,
    generate: bool = True,
) -> None:
    root = project_root.resolve()
    if generate:
        result = generate_docs(root)
        docs_dir = result.output_dir
        project_name = result.project_name
    else:
        docs_dir = root / "docs"
        project_name = root.name

    index_path = docs_dir / "index.html"
    if not index_path.exists():
        raise FileNotFoundError(
            f"No Docsify index found: {index_path}. Run `lantern docs` first."
        )

    handler = functools.partial(
        SimpleHTTPRequestHandler,
        directory=str(docs_dir),
    )
    server = ThreadingHTTPServer((host, port), handler)

    display_host = "localhost" if host == "0.0.0.0" else host
    url = f"http://{display_host}:{port}/"
    print(f"\n  AgentLantern Docs — {project_name}", flush=True)
    print(f"  Open: {url}", flush=True)
    print(f"  Files: {docs_dir}", flush=True)
    print("  Press Ctrl+C to stop.\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AgentLantern web server.")
    finally:
        server.server_close()
