// Shapes shared by every tier.

/** YYYY-MM-DD. */
export type IsoDate = string;

/** A claim's address, one grammar across all tiers (REF_PATTERN in caps.ts):
 *
 *    sha              7-40 hex       a commit
 *    path             repo-relative  a file
 *    #NN                             an issue
 *    urls/<name>                     a file in the urls tier; URLs never inline
 *    po:SNN                          a verbal ruling, by session
 *    <person>:<date>                 a human said it, and when
 *    <date>                          noted on that date, source unknown
 *    ''               blank          no source known
 *
 * Blank is COUNTED, never failed. Failing blanks buys fabricated refs, which are worse
 * than missing ones: a fabricated ref survives a sweep.
 *
 * A memory record is a CLAIM about a source, never a source. Open the ref before citing it
 * in another artifact.
 */
export type Ref = string;
