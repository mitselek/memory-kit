// Lessons: memory/lessons/<slug>.md, indexed by memory/lessons/index.yaml.
//
// Read at the moment of use, not on spawn -- which is why the body is free and only the
// index line is capped. A lesson carries its WHY; that is what distinguishes it from a rule.

import type { IsoDate, Ref } from './memory-common';

export interface LessonIndexFile {
  /** GENERATED from the lesson files, never hand-carried.
   *  A hand-maintained index is where staleness accumulates: the body stays right while the
   *  one-line summary rots, and the summary is what gets read. */
  lessons: LessonIndexLine[];
}

export interface LessonIndexLine {
  /** Filename without extension. */
  slug: string;
  /** <= LESSON_INDEX_LINE_CAP. What the lesson is for, not what it says. */
  summary: string;
  learned: IsoDate;
  ref: Ref;
  /** How this lesson is actually enforced -- stated, never assumed:
   *    'hooked'      a harness adapter fires it on a declared trigger
   *    'linted'      a check refuses the output that would violate it
   *    'recognition' nothing fires it; it works only if the reader remembers
   *  The kit defines the DECLARATION of a trigger; firing it is an adapter's job, because
   *  hook mechanisms belong to a harness, not to the convention. */
  enforcement: 'hooked' | 'linted' | 'recognition';
  /** Present when enforcement is 'hooked': what the adapter matches on.
   *  Tool-shaped only. A belief-shaped lesson has no trigger and should say so. */
  trigger?: string;
}

// Body shape (markdown, free): When -- Why -- What to do -- What not to do.
// Counting 'recognition' lessons honestly is the point of the enforcement field: a corpus
// where everything is recognition-only is a corpus that fires nothing.
