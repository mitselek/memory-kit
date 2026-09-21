# Changelog

## Unreleased

- Charter (Phase 0), 2026-09-21: rulings recorded, layout targeted, nothing implemented.
- ADOPTION.md and UPGRADE.md added 2026-09-21 as executable prompts. Minor upgrades are pull-only by contract.
- Ruling 2026-09-21: core/ ships universal rules + lessons; capped at 8 rules, each citing its incident, opt-out recorded. Types are generated from the schema, never hand-written.
- Ruling 2026-09-21: the household (Passepartout) drives the kit -- synthesizer and first adopter; FR contributes and reviews.
- Ruling 2026-09-21: tooling is python3 + PyYAML (parsing, schema generation) and awk (caps). No yq, no node.
- Ruling 2026-09-21: the kit is model- and harness-agnostic. Harness mechanisms live in adapters, never in the core.
