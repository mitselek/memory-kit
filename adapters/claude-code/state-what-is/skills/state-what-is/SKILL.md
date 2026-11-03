---
name: state-what-is
description: Find and fix text that narrates how a document changed, or points at ideas the reader never saw, instead of stating what is. Use before publishing or committing a design, spec, protocol, README or artifact you revised; after you changed your mind on a design choice; and when the user says "sweep", "state what is", "you keep referencing the old idea", or asks why a doc talks about something that isn't there. Works on English and Estonian text, and flags Jira keys the reader can't follow. Also flags vestigial rules that exist only to manage a dropped idea.
---

# State what is

A published text states what is. Its failure mode is a ghost draft: an earlier version of an idea that keeps showing through the final text. The writer stated something, changed their mind, and kept referring to the first idea, even though readers only ever see the final version. The cause is the **curse of knowledge**: the writer can't forget the draft, so they assume the reader knows it too. In documents it shows up as **narrating the diff**. In designs it shows up as **vestigial machinery**: rules kept alive to manage an idea whose premise has already fallen (escalation of commitment).

How a text got where it is belongs in the commit message, the changelog or the decision log.

## What to look for

| Kind | Looks like | Fix |
|---|---|---|
| Narrating the diff | "no longer", "now does", "after all", "this reverses…", "was dropped", "originally", "not adopted", "v0.4 makes…" in body text; in Estonian "enam ei", "varem", "algselt", "nüüd on", "loobusime", "asendati" | State the current design. Move the history to the commit message or log. |
| Ghost reference | an id, option, field or file the reader can't find: "no K28 vector", "option D", a deleted path, a Jira key with no link (`VEO-234`) | Delete it, define it where the reader can see it, or link the key. |
| Defensive absence | "X isn't in the body" answering a question only the writer asked | Say where X *is*, positively, or delete it. Keep absence statements that are rules ("never…") or scope ("this doesn't include…"). |
| Vestigial machinery | rules, flags, checks or prose that exist only to keep a dropped idea working | Remove the premise and ask whether each rule still has a job. Delete those that don't, then sweep every reference to them. |
| Version story in the body | headers like "Version 0.5: any OS", "as of v0.3" inside normative text | Keep the version number and stamp; put the story in the README status or changelog. |
| Thinking leaking into replies | "I considered X but…", where X only ever existed in your reasoning | In replies, mention only options the user has seen. |

**History is legitimate** in decision logs, changelogs, commit messages, README status lines, and evidence. Evidence is a real external event cited as a reason, such as "2.1.178 silently removed TeamCreate". It differs from narration of our own drafting.

## Procedure

1. **Scan.** Run `python3 -I <this skill's folder>/scan.py --ids FILE...` (the script sits next to this file; `--help` prints its usage). It prints candidate lines in six categories: `narration`, `narration-et`, `version-in-body`, `absence`, `unlinked-key` (a Jira key never linked in that file) and `single-use id`. Every line is a candidate, not a verdict. The `absence` category is noisy by design.
2. **Read the premise list.** For each decision you reversed in this piece of work, write the dropped idea down in one line. Then grep for its name and its machinery (field names, flags, commands, sections). The scanner can't know your premises; this step finds vestigial machinery.
3. **Classify each hit** with the table above. Use one test for every hit: **would a cold reader, who has only the final text, miss this sentence?** If not, it's a ghost.
4. **Fix.**
   - Rewrite narration as present-tense statements of the design.
   - Delete ghosts and dead machinery, and re-grep their names until nothing refers to them.
   - Move any history worth keeping to the commit message.
5. **Report.** Give one line per fix (file:line, kind, what you changed), and say what you left on purpose (rules, scope, evidence).
6. **Re-scan** once. The remaining hits should all be ones you judged legitimate.

## Examples (from Kaaslane, 2026-11-03)

- **Vestigial machinery.** The field `approved_by_human` couldn't be verified by a receiver. v0.4 still built a stamping client, a hash check and receiver trust rules around it. The fix deleted the field. Messages read as "X's assistant writes" unless a human countersignature proves "X writes". Of the machinery, the hash-checked prompt survived, because it still has a job: the human confirms the exact text.
- **Narrating the diff.** "A prod-llm window like 2026-10-22 no longer stops mail." became "A maintenance window like prod-llm's on 2026-10-22 doesn't stop mail."
- **Ghost reference.** "No new test vector after all" referred to a K28 vector that existed only in chat. In a published log, state the fact: "Client vectors test opening an envelope; a pin refusal is local client state."
- **Defensive absence.** "The message's own Lelle uuid isn't in the body" became "The message's own Lelle uuid lives in the envelope and the signed seal."
- **Diff against another doc.** "This reverses hr2's `latest` for a fleet" was deleted. The reasons for pinning stand on their own.

(*FR:Aen*)
