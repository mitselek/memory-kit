# Context discipline: checkpoints and a timely retire

Optional, not core (kit #68). A long session gets dearer and less reliable as its context fills:
every turn re-reads all of it, a prompt-cache expiry makes the next turn pay it in full, and
whatever lives only in the conversation is lost at compaction or when the window is replaced. The
kit's memory is what a fresh session resumes from; this page says when to write it down, and when
to stop.

## The rule

- **Checkpoint** at 50, 60 and 70% of the model's context window, the first time each is crossed.
- **Retire** at 80%, right after a checkpoint, while it is still fresh.

The marks are the home's choice. These are the household's, in daily use since 2026-10-14.

## The checkpoint routine

Done at once, without stopping the work:

1. Regenerate scratchpad `current` (cap 15) so it holds the task in flight and its next step. The
   rest goes to `staging` or a durable tier; `current` is rewritten, never appended to.
2. Run the lint gate.
3. Reread `current` cold, as a fresh session would: is the interrupted task there, with its next
   step? If not, fix it now.
4. Commit and push the home.

After a checkpoint, a fresh session could resume from `current` with nothing living only in the
conversation.

## Retiring

How a session ends and a fresh one starts is the home's own plumbing (ruled 2026-11-01); the kit
gives the marks and the routine, not the mechanism. One example, the household's: the session
touches a marker file and exits; a resident tmux loop sees the marker and relaunches the harness
with a fresh window, and the fresh session's start routine re-orients from `current`. Whatever
the mechanism, it must not take the operator's terminal down with the session.

## Measuring

- Measure against the **model's context window**: the used share is the newest model response's
  input side (input + cache-write + cache-read tokens) over the window. Output is left out.
- **Claude Code:** the watch plugin reads that figure exactly from the session and reports once
  per mark (`watch_context_percent`). With `watch_context_step` the report quotes the home's own
  step, so the ring says what to do. See `adapters/claude-code/watch/README.md`.
- **Other harnesses:** any gauge that reads the same figure will do. The routine itself is
  harness-free.

```yaml
# memory-kit.conf, Claude Code
watch_context_percent: 50, 60, 70, 80
watch_context_step: "50, 60, 70: run the checkpoint routine (memory-kit/CONTEXT.md); 80: checkpoint, then retire by this home's step"
```

## Cost

Every watch report is a full turn (kit #17), so four marks cost four turns a session. Declare only
the marks the home acts on.
