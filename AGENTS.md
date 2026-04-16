# AGENTS.md

## Root Orchestrator
This root agent is the coordinator for all scoped agents in this repository.

## Coordination Rules
1. Route requests only to the minimum required agent(s).
2. Do not trigger broad cross-domain work unless a change explicitly spans domains.
3. Keep branch history clean and small; one purpose per commit when possible.
4. Ensure affected documentation is updated for every behavioral change.
5. Escalate to `.git-agent` for release notes, bug logs, and source-control hygiene.

## Agent Map
- `data/AGENTS.md`: research + structured data curation.
- `functions/AGENTS.md`: functional behavior and runtime logic.
- `ui/AGENTS.md`: theme, readability, spacing, and visual UX standards.
- `assets/AGENTS.md`: image/audio/static asset quality and organization.
- `automation/AGENTS.md`: build/release automation for macOS and Windows.
- `documentation/AGENTS.md`: docs, changelog, diagrams, and source attributions.
- `.git-agent/AGENTS.md`: git flow, change tracking, and bug/change reporting cadence.

## Change Routing
- Tone math, pedal order research, scale datasets: `data`.
- Drag/drop, controls, event handling, persistence logic: `functions`.
- Theme palettes, typography, layout readability: `ui`.
- Guitar/pedal art and binary assets: `assets`.
- Build scripts, architecture targets, packaging: `automation`.
- User/developer docs and diagrams: `documentation`.
- Branching, commit strategy, changelog sync, bug timeline: `.git-agent`.
