// Obligations: memory/obligations.yaml. Strict YAML.
//
// An obligation is a claim about what SOMEONE MUST DO -- "waiting on X", "ball with Y",
// "owed to Z". It is not a fact, and the difference is the failure mode:
//
//   a fact rots when the WORLD changes and nobody looked
//   an obligation rots when the COUNTERPARTY ACTS and nobody looked
//
// So an obligation does not want a refutation address. It wants an owner, a resolution
// check, and an expiry. "Prove this wrong" is the wrong question; "has it been done yet?"
// is the right one, and the answer usually lives somewhere the actor already wrote it.
//
// Evidence for the tier (kit issue #1 and the Passepartout household, both 2026-09):
// three wrong claims inside one hour -- two ledger issues reported open after the human
// closed them, one PR "ball with X" five days after it merged; and in the household, a
// draft reported as waiting hours after it was sent, and a mail reported as sent when it
// had bounced. Every one was TRUE when written. None was a fact.

import type { IsoDate, Ref } from './memory-common';

export interface ObligationsFile {
  obligations: Obligation[];
}

export interface Obligation {
  /** What is owed, in one line. State the deliverable, not the feeling about it. */
  obligation: string;
  /** Who must act for this to resolve. A role or a name -- never "us" without saying who.
   *  If this home must act, say so: an obligation with no named actor is a wish. */
  actor: string;
  /** When it started. Not when it was written down -- when the waiting began. */
  since: IsoDate;
  /** HOW TO FIND OUT WHETHER IT IS ALREADY DONE: a command, a page, a person to ask.
   *  This is the field the tier exists for. An obligation without a check is a claim that
   *  will be wrong before anyone notices.
   *  Blank is permitted and counted -- some waiting genuinely has no observable signal --
   *  but a blank check means the obligation must be resolved by asking, and the expiry is
   *  then the only thing protecting the reader. */
  check: string;
  /** When this stops being believable regardless of what the actor did.
   *  On expiry: run the check, then re-state, resolve, or hand it to a human. Never renew
   *  an obligation silently -- silent renewal is how a three-day wait becomes a quarter. */
  expires: IsoDate;
  /** Origin: who said this was owed, and when. */
  ref: Ref;
}

// Resolved obligations are DELETED, not annotated. If the resolution mattered, it became a
// fact, a lesson or a ruling -- and those tiers know how to keep it.
//
// An obligation is never the ledger. If a real ledger exists -- an issue tracker, a
// contract, a shared board -- this tier holds the pointer and the check, never a copy of
// the state. A copy is a second source of truth that cannot be corrected by the people who
// own the first.
