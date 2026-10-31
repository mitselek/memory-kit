# memory

This home's memory. Shape: `memory-kit/types/*.ts`. Lint: `memory-kit/lint/memory-lint.sh`.

The kit owns `memory-kit/`; this directory is yours. They never interleave, so a kit upgrade
never touches anything here.

| path | tier | read when |
|------|------|-----------|
| `<name>.yaml` | scratchpad | every session start |
| `rules.yaml` | rules | every session start |
| `obligations.yaml` | obligations | when something is owed, and on its expiry |
| `commitments.yaml` | commitments (optional; create it to opt in) | when a trigger happens: it creates an obligation |
| `facts/` | facts | when the subject comes up; swept on a cadence |
| `dormant/` | parked facts | only when a `reviewed` date says so |
| `lessons/` | lessons | at the moment of use |
| `urls/` | urls | when a ref points here |
| `secrets/` | secrets | when a consumer needs one |
| `keys.yaml` | keys | when granting or revoking access |

## Caps at the moment of writing (source: caps.yaml)

These tiers have no README of their own. The gate fails a record over its cap.

- Scratchpad `current`: at most 15 rows (`scratchpad.current_rows`).
- Scratchpad `current` plus `staging`: at most 100 rows (`scratchpad.total_rows`).
- Scratchpad record text: at most 100 characters (`scratchpad.record_chars`).
- Rules: at most 20 rows (`rules.rows`).
- One rule: at most 100 characters (`rules.rule_chars`).
- An obligation text: at most 120 characters (`obligations.obligation_chars`).

Fact, dormant and lesson caps are in those folders' READMEs.

## A home born on the kit

A home that started from this skeleton has no `adoption/` folder and was never converted. The
gates in `ADOPTION.md` are not for it. The core rules apply from its first day, including this
one: a refuted fact is deleted, not annotated. Git is the archive.

Two things this directory is not: a ledger (point at the real one and record how to re-check
it) and an archive (git is the archive -- refuted facts are deleted, not annotated).
