# lessons

Situational knowledge with a why: read at the moment of use, not on spawn. That is the whole
reason bodies are free while rules are capped.

`index.yaml` is generated from the files. Never hand-carry it -- a hand-kept index rots while
its bodies stay right, and the index is what gets read. Each lesson opens with YAML front
matter holding its index fields (`summary`, `learned`, `ref`, `enforcement`, `trigger`);
`tools/lesson-index.py` writes the index from them and `--check` reports a stale one. The lint
fails a lesson with no front matter and an index row that differs from it.

Each lesson states how it is enforced: hooked, linted, or recognition-only. A corpus where
everything is recognition-only fires nothing.

## Caps at the moment of writing (source: caps.yaml)

- Lesson summary: at most 120 characters (`lessons.index_line_chars`). Check the length before you
  run `tools/lesson-index.py`; the gate fails a longer one.
- A ref may be a path, so `@` is allowed in it: `/usr/local/lib/node_modules/@anthropic-ai/claude-code`.
