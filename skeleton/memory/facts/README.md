# facts

Claims about the PRESENT state of the world, each with an address where a sweep can prove it
wrong. One file per subject; the filename names the subject, never the moment. `ls` is the index.

`verified` is the date a fact last SURVIVED a refutation attempt, not a birthday. Age is a
queue here, because every item carries a test.

If proving it wrong would be a new decision rather than a discovery, it is not a fact.

## Writing a refute

A refute says where to prove the fact WRONG. It comes in two kinds. `"=ref"` means the ref
itself is the test.

**A lookup.** A path, an address, or a command whose output a reader judges: open it expecting to
be contradicted. Examples: `curl <api> ...`, `Gmail thread <id> (sender, date)`, `ask <person>`.
This is valid, and it is the common case.

**A check.** A command whose exit status decides, for unattended sweeps. If you write a refute as a
check, exit 0 means the fact is WRONG (refuted) and non-zero means it survived. This is the
opposite of most tests; invert with `!` where needed. Example, for the fact "git is installed" with
ref `/usr/bin/git`: `refute: "/usr/bin/test ! -e /usr/bin/git"` exits 0 only if git is gone, so
exit 0 means the fact is wrong.

**The shell.** Write a check for a plain `sh -c` with full paths. An agent's own interactive shell
may wrap grep or find: in Claude Code, `grep` is a shell function and `find` runs bfs. Use full
paths (`/usr/bin/grep`) or test the check under `sh -c '...'` before you save it.

**Dead links and facts about absence.** A ref that does not resolve is a dead link only when the
fact claims the thing exists. For a fact about absence ("git is not installed", ref
`/usr/bin/git`) the missing path is the evidence. Read what the fact claims and run the refute
before you delete anything.

## Caps at the moment of writing (source: caps.yaml)

- Facts per file: at most 30 (`facts.per_file`). Overflow starts a new subject file.
- Words per fact: at most 42 (`facts.fact_words`).
