# automation/AGENTS.md

## Mission
Automate consistent builds and packaging across supported platforms.

## Scope
- Build scripts for macOS (arm64, x86_64, universal2) and Windows.
- Repeatable packaging steps with clear output paths and backups.
- CI-ready command surfaces for future pipeline integration.
- Release checklist integration with documentation and `.git-agent`.

## Output Expectations
- Commands should be non-interactive and scriptable.
- Fail fast with clear errors.
- Keep app artifact locations predictable.
