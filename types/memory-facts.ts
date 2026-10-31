// Facts: memory/facts/<subject>.yaml. One file per subject; the filename names the subject,
// never the moment. `ls` is the index.

import type { IsoDate, Ref } from './memory-common';

export interface FactsFile {
  facts: Fact[];   // <= FACTS_PER_FILE; overflow mints a new subject, never blocks a write
}

export interface Fact {
  /** One present-tense sentence, <= FACT_WORD_CAP words. */
  fact: string;
  ref: Ref;
  /** Where to prove it WRONG. REFUTE_SAME_AS_REF when the origin is the test. Blank = no test
   *  known; counted. Two kinds:
   *  a lookup -- a path, an address, or a command whose output a reader judges; the common case.
   *  a check -- a command whose exit status decides, for unattended sweeps. Written as a check,
   *  exit 0 means the fact is WRONG (refuted) and non-zero means it survived; invert with `!`
   *  where needed. Write it for a plain `sh -c` with full paths: an agent's interactive shell may
   *  wrap grep or find (in Claude Code, `grep` is a function and `find` runs bfs). */
  refute: string;
  /** Last date it SURVIVED a refutation attempt. Not a birthday. */
  verified: IsoDate;
}

// A ref that does not resolve is a dead link only when the fact claims the thing exists. For a fact
// about absence ("git is not installed", ref /usr/bin/git) the missing path is the evidence: run the
// refute before deleting.
// Refuted facts are deleted; git is the archive. Age of `verified` is a queue for this tier.
// Which tier a claim belongs to, by how it rots: lessons/the-genus-of-a-claim.md
