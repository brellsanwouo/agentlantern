from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def read_metadata(root: Path) -> dict[str, Any]:
    path = root / "pyproject.toml"
    if not path.exists():
        return {}
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
        result = data.get("project", {})
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def read_contacts(root: Path) -> list[dict[str, str]]:
    metadata = read_metadata(root)
    authors = metadata.get("authors", [])
    contacts = []
    if isinstance(authors, list):
        for author in authors:
            if not isinstance(author, dict):
                continue
            name = str(author.get("name", "")).strip()
            email = str(author.get("email", "")).strip()
            if name or email:
                contacts.append({
                    "name": name or "not declared",
                    "email": email or "not declared",
                })
    return contacts


def has_placeholder_contact(root: Path) -> bool:
    for contact in read_contacts(root):
        if contact["name"] == "Your Name" or contact["email"] == "you@example.com":
            return True
    return False
