# data/AGENTS.md

## Mission
Research and maintain all app data used for recommendations, music theory, and order-dependent tone behavior.

## Scope
- Pedal parameter research by style and guitar/amp context.
- Signal-order interaction research (e.g., SD-1/DS-1 stacking, EQ placement effects).
- Music theory datasets (scales, interval formulas, key charts, progression heuristics).
- Sources and confidence notes for every major dataset.

## Deliverables
- Machine-readable data files (`.json`) consumed by runtime code.
- Clear schema comments in companion markdown when needed.
- Incremental updates without breaking downstream consumers.

## Constraints
- Prefer additive updates and backward-compatible keys.
- Track assumptions and cite sources in `documentation/SOURCES.md`.
