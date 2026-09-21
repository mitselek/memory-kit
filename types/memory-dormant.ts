// Dormant facts: memory/dormant/<subject>.yaml.
//
// A fact PARKED, not deleted: out of play, may return. Exempt from the live sweep; revisited
// on the cadence `reviewed` states. Parking moves ONE fact, not a whole subject file.

import type { Fact, FactsFile } from './memory-facts';

export interface DormantFile extends FactsFile {
  facts: DormantFact[];   // <= DORMANT_PER_FILE
}

export interface DormantFact extends Fact {
  /** Why it is parked. */
  parked: string;
  /** How and when to check whether it should return. */
  reviewed: string;
  // `verified` inherits its meaning: the last time `reviewed` was actually done.
}

// A fact that something live still cites is not dormant.
// A truly dead fact is deleted, not parked. Git is the archive.
