// Core content: what ships WITH the kit and is installed into every adopting home, so the
// home's assistant knows what its own convention is, where it came from, how to upgrade it
// and how to talk back -- without needing anything external.
//
// core/facts/  holds facts about the KIT only. A fact is a claim about a particular present,
//              so a fact about a home is never universal.
// core/rules.yaml is capped hard: every row is read on every spawn in every adopting home.
// core/lessons/ is uncapped -- read at the moment of use, not on spawn.
// core/urls/   one URL per file; core content cites the short name, never an inline URL.

import type { Fact } from './memory-facts';
import type { Rule } from './memory-rules';

export interface CoreRulesFile {
  rules: CoreRule[];   // <= CORE_RULES_CAP
}

export interface CoreRule extends Rule {
  /** mandatory = the kit's own operation; a home cannot opt out of knowing where its kit
   *  comes from. optional = hygiene; a home may disable it by naming it with a reason in
   *  its config, and the lint REPORTS the divergence rather than forbidding it. */
  core: 'mandatory' | 'optional';
  /** The specific, repeated, recorded mistake a home would make without this rule.
   *  Admission test for core. No incident, no core -- it is a lesson, and lessons are free. */
  incident: string;
}

export interface CoreFactsFile {
  facts: Fact[];   // <= CORE_FACTS_CAP; about the kit itself only
}

// Additions to core are subtractive by default: a proposal must argue why it is not a
// lesson, and -- core being full -- name what it displaces.
