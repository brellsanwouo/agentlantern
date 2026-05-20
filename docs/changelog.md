# Changelog

AgentLantern follows early-project semantic versioning: minor versions may still refine command behavior, while patch versions should stay focused on fixes, docs, and small CLI additions.

## v0.1.21

Released from the current `main` branch.

### Added

- `lantern replay last` opens the newest saved replay from `.lantern_replays/`.
- Official docs now expose the current version in the top navigation.
- Changelog page added to track product changes from the documentation site.

### Improved

- Home page logos now resolve correctly on GitHub Pages.
- Home page includes framework support badges:
  - CrewAI is marked as available.
  - LangGraph, AutoGen, Smolagents, and Google ADK are marked as coming soon.
- Replay documentation now covers named replays, direct `.jsonl` paths, and latest replay playback.

### Changed

- `lantern web` serves generated docs over local HTTP on port `9000` by default.
- `lantern play` documents UI port `7891` and WebSocket port `7890`.

## v0.1.20

### Changed

- Project docs serving moved away from self-signed local HTTPS.
- Documentation commands were clarified around default project paths and ports.

## v0.1.0

Initial public package direction.

### Added

- `lantern docs` for generating agent-project documentation.
- `lantern web` for generating and serving project docs.
- `lantern lint` for deterministic agent-project checks.
- `lantern inspect` for JSON project inspection.
- `lantern play` for live animated CrewAI run visualization.
- `lantern replay` for replaying saved Play runs.
