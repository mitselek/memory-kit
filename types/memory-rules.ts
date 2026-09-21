// Rules: memory/rules.yaml. READ ON SPAWN, so they cost every session forever -- hence few
// and short. A rule is a standing norm; its origin (a ruling, an incident) lives in `ref`.

import type { Ref } from './memory-common';

export interface RulesFile {
  rules: Rule[];   // <= RULES_CAP
}

export interface Rule {
  /** Imperative, <= RULE_CHAR_CAP. */
  rule: string;
  ref: Ref;
}

// A rule that is really a lesson -- needs a why, fires on a situation rather than always --
// goes to memory/lessons/ and leaves at most one index line here.
//
// Split from lessons by WHEN IT IS READ, not by importance: rules are read on every spawn,
// lessons at the moment of use. That is the whole reason rules are capped and lessons are not.
