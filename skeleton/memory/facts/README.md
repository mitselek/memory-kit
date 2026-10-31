# facts

Claims about the PRESENT state of the world, each with an address where a sweep can prove it
wrong. One file per subject; the filename names the subject, never the moment. `ls` is the index.

`verified` is the date a fact last SURVIVED a refutation attempt, not a birthday. Age is a
queue here, because every item carries a test.

If proving it wrong would be a new decision rather than a discovery, it is not a fact.

## Writing a refute

A refute is a command or a path. `"=ref"` means the ref itself is the test.

**Exit codes.** A command refute that exits 0 means the fact is WRONG (refuted). A non-zero exit
means the fact survived. This is the opposite of most tests. Example, for the fact "git is
installed" with ref `/usr/bin/git`: `refute: "/usr/bin/test ! -e /usr/bin/git"` exits 0 only if
git is gone, so exit 0 means the fact is wrong.

**The shell.** Write a refute for a plain `sh -c` with system tools. An agent's own interactive
shell may differ: in Claude Code, `grep` is a shell function and `find` runs bfs. Use full paths
(`/usr/bin/grep`) or test the refute under `sh -c '...'` before you save it.

**Dead links and facts about absence.** A ref that does not resolve is a dead link only when the
fact claims the thing exists. For a fact about absence ("git is not installed", ref
`/usr/bin/git`) the missing path is the evidence. Read what the fact claims and run the refute
before you delete anything.

## Caps at the moment of writing (source: caps.yaml)

- Facts per file: at most 30 (`facts.per_file`). Overflow starts a new subject file.
- Words per fact: at most 42 (`facts.fact_words`).
