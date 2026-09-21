// Scratchpad: memory/<name>.yaml. Strict YAML: every key on every record, blanks left blank.
//
// No session narrative. A transcript converted into this tier either becomes a record in a
// tier or is dropped; git is the archive and the primary artifact is the source.

import type { Ref } from './memory-common';

export interface Scratchpad {
  /** Act on these next session. <= CURRENT_CAP.
   *  REGENERATED at close, never appended -- this is what keeps it honest. */
  current: ScratchpadRecord[];
  /** Do not re-derive these. Staging for promotion into a durable tier, not an archive. */
  staging: ScratchpadRecord[];
}

/** One idea. Does not fit? It is two records. */
export interface ScratchpadRecord {
  label: Label;
  /** <= RECORD_CHAR_CAP. No URLs -- cite urls/<name>. */
  record: string;
  ref: Ref;
}

export type Label =
  | 'DECISION' | 'LEARNED' | 'WARNING'
  | 'WIP' | 'DEFERRED'
  | 'PATTERN' | 'GOTCHA';

// No date field: a date is PROVENANCE and belongs in `ref` (<person>:<date>, or a bare
// <date> for "noted, no source"). A birthday on every row invites age-as-a-queue, which is
// wrong for a tier whose rows are judgment rather than tested claims.
//
// CHECKPOINT is not a label: `current` is regenerated from truth, so it has no job.
//
// Two caps, not one: a row cap alone displaces growth into longer rows.
// See the rationale in caps.ts.
