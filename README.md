# memory-kit

One memory convention for AI agents that live somewhere -- a household, a team, a seed
that others clone. One repo; consumers pin a version and upgrade deliberately.

Consumers at charter (2026-09-21):

- **ai-locum** -- the seed a human clones to grow a household assistant (Codeberg, beside this repo)
- **framework-research** -- a ten-seat research team (github.com/mitselek/ai-teams)
- **Passepartout** -- the household reference implementation the seed was cut from

Why: the convention lived as code in two places and diverged in four of seven tiers within
five sessions. Three implementations of one idea is the failure mode this repo removes.

## Rulings (PO, 2026-09-21)

| # | Ruling |
|---|--------|
| D1 | Strict YAML for every structured tier (scratchpad, facts, dormant, rules, lessons index, keys). Markdown only for prose bodies. `urls/` stay one-line files; secrets stay `.age`. |
| D2 | **Fixtures are the contract.** Every implementation passes the same `fixtures/{valid,invalid}/`. JSON Schema is the machine-readable statement; `SPEC.md` the readable one. A schema can be reinterpreted; a fixture cannot. |
| D3 | Distributed by `git subtree` into `memory-kit/` in each consumer, with `VERSION` and `sync.sh`. Never a submodule. |
| D4 | Codeberg is primary; GitHub carries a mirror. |
| D5 | Proven-first: nothing enters the kit unproven in at least one consumer. Semver; a migration script per major. See `GOVERNANCE.md`. |
| D6 | Core tiers only in v0.x: scratchpad, facts, dormant, rules, lessons, urls, secrets, keys. Refute-by-genus ships as guidance. Team-only artefacts stay with their team until a second consumer wants them. |
| D7 | One lint, two modes: `--gate` (fail-closed) and `--report` (exit 0). One principle: **a gate must pass on the tree it is introduced to.** A fresh home gates everything from day one; an existing home gates what already passes and gauges the rest. |

Resolved questions:

- No date field on records. A date is provenance and lives in `ref`: `<person>:<date>`, or a bare
  `<date>` for "noted, no source". **Provisional** -- judged on the household migration in practice.
- Session transcripts are dropped on conversion; rows convert into a tier or die. **Provisional**, same test.
- Harness-managed auto-memory stays outside the kit; each consumer states that boundary as a fact.
- Phase 1 is authored by framework-research (Aen), reviewed by Passepartout.

## Ref grammar

`sha | path | #NN | urls/<name> | po:SNN | <person>:<date> | <date> | blank`

Blank is counted, never failed -- failing it buys fabricated refs. `refute: "=ref"` means the
origin doubles as the test.

## Layout (target for v0.1)

```
SPEC.md            the convention, readable
schemas/           one JSON Schema per tier
caps.yaml          every numeric cap, in one place
fixtures/          valid/ and invalid/ samples per tier -- the contract
lint/              reference lint: POSIX sh + awk + yq, --gate | --report
migrations/        one directory per breaking version
skeleton/          the empty home a fresh consumer starts from
lessons/           convention-level lessons that travel with the kit
templates/         secrets README, keys file
VERSION            pinned by consumers
CHANGELOG.md
```

## Status

Phase 0 -- charter. Nothing but this README, `GOVERNANCE.md`, `VERSION`, `CHANGELOG.md`.
Plan of record: `ai-teams/designs/new/memory-kit/plan.md`. Discussion: ai-teams #122.
