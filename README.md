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
- **The household drives the kit** (PO ruling, 21.09 -- supersedes the earlier Q6): Passepartout
  synthesizes and authors; framework-research (Aen) contributes the shapes it has run and reviews;
  every convention is adopted by the household FIRST, then the seed, then the team. Proven-first
  starts at home.

## Model- and harness-agnostic (ruled 2026-09-21)

The kit is memory conventions, not an agent framework. It must hold for any model on any
harness: plain files, plain formats, no vendor mechanism anywhere in the core.

Binding consequences:

- **No harness mechanism in the kit.** Tool-call hooks, skill manifests, agent-spawn shapes and
  session lifecycles belong to a harness, not here. A lesson may *declare* a trigger; firing it
  is an adapter's job, supplied by the consumer.
- **No vendor paths in normative text.** "The harness's own memory directory", never a literal
  `~/.<vendor>/...`. Examples are marked as examples.
- **Adapters, where a harness must be named.** One file per harness, outside the core
  (`adapters/<harness>.md`), carrying that harness's hard facts. Pattern proven in ai-locum.
- **Tooling stays language-level**, not model-level: python3 + PyYAML, awk, git. Nothing that
  assumes a particular assistant is reading.

Test for anything proposed: *would this still make sense for a different model, on a different
harness, in a different language?* If not, it is an adapter or a consumer's business.

**Worked example -- playbooks vs skills.** A home's domain procedures (how to triage mail, how
to tend the box) are plain markdown files, read when a procedure calls for them. Some harnesses
offer a native "skill" mechanism that would surface the same files automatically by description.
The kit does not adopt it: a skill manifest is a harness feature, and a home whose competence
is expressed as skills cannot be read by a harness that has none. Procedures stay plain files.
A harness with skills may wrap them in its adapter -- the file remains the source.

## Tooling (ruled 2026-09-21)

Parsing and schema generation: **python3 + PyYAML**. Line-shaped checks (row and char caps):
**awk**. Nothing else -- no `yq` (not present by default, and two different programs share the
name), no node (nvm installs sit outside the systemd/cron PATH, and the lint must run from cron).

The lint fails closed with a one-line install hint when PyYAML is missing; it never silently
skips a check.

## Ref grammar

`sha | path | #NN | urls/<name> | po:SNN | <person>:<date> | <date> | blank`

Blank is counted, never failed -- failing it buys fabricated refs. `refute: "=ref"` means the
origin doubles as the test.

## How a home uses this

- **Adopting**: clone or subtree the kit, then have the assistant execute `ADOPTION.md`. It is a
  prompt, not a guide -- the assistant does the work and stops at three gates that are the
  human's to rule: the tier mapping, the rules cut list, and any deletion. Adoption runs once.
- **Upgrading**: pull, then have the assistant execute `UPGRADE.md`. **A minor upgrade is a pull
  and nothing else** -- no minor may change the shape of data already on disk. Anything that
  would is a major, and ships `migrations/<version>/`.
- **Boundary**: the kit owns `memory-kit/`; the home owns its memory directory. They never
  interleave, and the home's config for the kit lives outside the subtree, where a pull cannot
  clobber it. If an upgrade needs to reach into the home's data, the kit has leaked.

## Layout (target for v0.1)

```
ADOPTION.md        prompt: bring an existing home onto the kit, once
UPGRADE.md         prompt: after every pull
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
First adopter and synthesizer: Passepartout (the household). Phase 1 begins with its own migration.
Plan of record: `ai-teams/designs/new/memory-kit/plan.md`. Discussion: ai-teams #122.
