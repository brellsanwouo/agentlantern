from __future__ import annotations

import json
import sys
from pathlib import Path

from agentlantern.frameworks.registry import detect_framework


_ICONS = {"error": "✗", "warning": "△", "info": "·"}
_ORDER = {"error": 0, "warning": 1, "info": 2}


def run_lint(project_root: Path, *, strict: bool = False, as_json: bool = False) -> None:
    root = project_root.resolve()
    analyzer = detect_framework(root)
    project = analyzer.analyze(root)
    findings = _get_findings(analyzer, project)

    if as_json:
        payload = {
            "project": project.name,
            "framework": project.framework,
            "root": str(root),
            "findings": [
                {
                    "severity": f.severity,
                    "code": f.code,
                    "message": f.message,
                    "location": f.location,
                    "file": f.file,
                    "line": f.line,
                }
                for f in sorted(findings, key=lambda f: _ORDER.get(f.severity, 9))
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if any(f.severity == "error" for f in findings) or (strict and findings):
            sys.exit(1)
        return

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    infos = [f for f in findings if f.severity == "info"]

    print(f"\nAgentLantern Lint — {project.name} ({project.framework})\n")

    if not findings:
        print("  No issues found.\n")
        return

    for finding in sorted(findings, key=lambda f: _ORDER.get(f.severity, 9)):
        icon = _ICONS.get(finding.severity, "?")
        location = f"  {finding.file}:{finding.line}  " if finding.file and finding.line else "  "
        print(f"  {icon}  [{finding.code}]{location}{finding.message}")

    print()
    parts = []
    if errors:
        parts.append(f"{len(errors)} error{'s' if len(errors) > 1 else ''}")
    if warnings:
        parts.append(f"{len(warnings)} warning{'s' if len(warnings) > 1 else ''}")
    if infos:
        parts.append(f"{len(infos)} info")
    print(f"  Summary: {', '.join(parts)}\n")

    if errors or (strict and findings):
        sys.exit(1)


def _get_findings(analyzer, project):
    if project.framework == "CrewAI":
        from agentlantern.frameworks.crewai.linter import lint_crewai
        return lint_crewai(project)
    return []
