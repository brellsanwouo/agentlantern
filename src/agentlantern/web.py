from __future__ import annotations

import functools
import shutil
import ssl
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agentlantern.docs import generate_docs

_SSL_DIR = Path.home() / ".agentlantern" / "ssl"
_CERT = _SSL_DIR / "cert.pem"
_KEY  = _SSL_DIR / "key.pem"


def _ensure_ssl_cert() -> tuple[Path, Path]:
    """Generate a self-signed cert in ~/.agentlantern/ssl/ if it doesn't exist."""
    _SSL_DIR.mkdir(parents=True, exist_ok=True)
    if _CERT.exists() and _KEY.exists():
        return _CERT, _KEY

    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError(
            "openssl not found on PATH. Install it (e.g. `apt install openssl`) "
            "or generate a cert manually and place it at:\n"
            f"  cert: {_CERT}\n"
            f"  key:  {_KEY}"
        )

    print("Generating self-signed SSL certificate (one-time)…", flush=True)
    subprocess.run(
        [
            openssl, "req", "-x509",
            "-newkey", "rsa:2048",
            "-keyout", str(_KEY),
            "-out",    str(_CERT),
            "-days",   "3650",
            "-nodes",
            "-subj",   "/CN=localhost",
        ],
        check=True,
        capture_output=True,
    )
    print(f"Certificate stored in {_SSL_DIR}", flush=True)
    return _CERT, _KEY


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

    cert, key = _ensure_ssl_cert()

    handler = functools.partial(
        SimpleHTTPRequestHandler,
        directory=str(docs_dir),
    )
    server = ThreadingHTTPServer((host, port), handler)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    server.socket = ctx.wrap_socket(server.socket, server_side=True)

    display_host = "localhost" if host == "0.0.0.0" else host
    url = f"https://{display_host}:{port}/"
    print(f"\n  AgentLantern Docs — {project_name}", flush=True)
    print(f"  Open: {url}", flush=True)
    print(f"  Files: {docs_dir}", flush=True)
    print(f"\n  Note: self-signed certificate — accept the browser warning once.", flush=True)
    print("  Press Ctrl+C to stop.\n", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AgentLantern web server.")
    finally:
        server.server_close()
