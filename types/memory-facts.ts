// Facts: memory/facts/<subject>.yaml. Strict YAML.
//
// A fact is a claim about the PRESENT state of the world, with an address where a sweep can
// prove it wrong. If proving it wrong would be a new DECISION rather than a discovery, it is
// not a fact -- see the genus note at the foot of this file.
//
// Filename names the SUBJECT, never the moment; `ls` is the index.

import type { IsoDate, Ref } from './memory-common';

export interface FactsFile {
  facts: Fact[];   // <= FACTS_PER_FILE; overflow mints a new subject, never blocks a write
}

export interface Fact {
  /** One sentence, present tense, <= FACT_WORD_CAP words. */
  fact: string;
  /** Origin. Ref grammar. Blank = no source known; counted, never failed. */
  ref: Ref;
  /** Where to go to prove this WRONG: a command, a path, an address.
   *  REFUTE_SAME_AS_REF ('=ref') when the origin doubles as the test.
   *  Blank = no test known; the claim rests on trust and the lint counts it. */
  refute: string;
  /** The date this last SURVIVED a refutation attempt. Not a birthday.
   *  A sweep opens `refute` EXPECTING contradiction, then re-stamps, corrects, or deletes. */
  verified: IsoDate;
}

// Refuted facts are DELETED, not annotated. Git is the archive.
//
// Age of `verified` IS a queue for this tier, because every item carries a test.
//
// GENUS -- which tier a claim belongs to, by how it rots:
//   rots by a clock, a source could contradict it    -> fact (give it a refute address)
//   goes inapplicable rather than false              -> lesson
//   rots only when re-decided                        -> a ruling; on reversal keep ONE dated
//                                                       line naming what replaced it
//   names someone you are waiting on                 -> not a fact: it flips silently when
//                                                       they act. Scratchpad row, with a
//                                                       command that re-checks it.
