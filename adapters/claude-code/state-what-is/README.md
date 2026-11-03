# state-what-is

A skill for Claude Code (kit #73), by framework-research (Aen), 2026-11-03. A published text
should state what is. This skill finds the places where a revised text still shows its drafts:

- **narration**: "no longer", "this reverses", "was dropped"; in Estonian "enam ei", "varem",
  "algselt";
- **ghost references**: an id defined nowhere, a Jira key with no link;
- **defensive absence**: "X isn't in the body", answering a question only the writer asked;
- **vestigial machinery**: rules kept alive only to manage an idea that was dropped.

It proposes rewrites that state the current design; the history goes to the commit message or
the changelog. The procedure and the examples are in
[`skills/state-what-is/SKILL.md`](skills/state-what-is/SKILL.md).

## Install

```sh
claude plugin install state-what-is@memory-kit
```

Then `/reload-plugins`. Installing it is the home's choice. A user-scope install puts the
skill's description in every session on the machine; the skill itself loads only when used.
See [Install scope](../README.md#install-scope-kit-35).

## The scanner

`skills/state-what-is/scan.py` works without the skill too: python3, stdlib only.

```sh
python3 -I skills/state-what-is/scan.py --ids design.md README.md
```

It prints `file:line: [category] match | context` per candidate, and the count on stderr. Every
hit is a candidate for a reader to judge, never a verdict. Known limits: the `absence` category
is noisy by design (most hits are legitimate "never" rules), and the scanner cannot know which
ideas a writer dropped, so the skill's procedure has the writer list them first.

## Develop

```sh
claude plugin validate .
python3 tests/scan-test.py      # also run by lint/run-fixtures.sh
```
