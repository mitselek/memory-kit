#!/usr/bin/env python3
"""Prompt-cache report from a home's Claude Code transcripts (kit #70; the household's tool, 20.10.2026).

    python3 -I cache-report.py [--home PATH] [--hours N] [--log FILE]

Reads the transcripts Claude Code keeps for the folder a session starts in (default: the current
folder; --home names another), under $CLAUDE_CONFIG_DIR/projects or else ~/.claude/projects as
Claude Code does (kit #72), and reports the main loop's API calls in the window (default: the
last 24 h):
- idle pings: calls after a gap of 45 min or more that found the cache warm (the watch's
  repeating idle report, kit #47);
- cold rebuilds: calls that wrote more than 50k tokens to the cache (the cache had expired, or a
  new session started);
- compactions: compact_boundary entries, with their trigger and size.
Cost figures are in base-price input tokens at assumed rates (cache read 0.1x, one-hour cache
write 2x). --log FILE appends one tab-separated row per run (a header first, if the file is new).
Stdlib only; writes nothing without --log. See CONTEXT.md, "Keeping the prompt cache warm".
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

PING_GAP_MIN = 45
COLD_WRITE = 50_000
READ_RATE, WRITE_RATE = 0.1, 2.0
NAME_MAX = 200          # Claude Code cuts longer folder names and appends a hash


def transcript_dirs(home):
    """Claude Code's folder for a session started in `home`: under its config folder
    ($CLAUDE_CONFIG_DIR, else ~/.claude), the absolute path with every character that is not a
    letter or a digit turned into '-' (2.1.317). Returns (the folder looked for, those found)."""
    config = os.environ.get("CLAUDE_CONFIG_DIR") or str(pathlib.Path.home() / ".claude")
    root = pathlib.Path(config).expanduser() / "projects"
    name = re.sub(r"[^a-zA-Z0-9]", "-", os.path.abspath(home))
    if len(name) <= NAME_MAX:
        return root / name, [root / name] if (root / name).is_dir() else []
    return root / (name[:NAME_MAX] + "-*"), sorted(p for p in root.glob(name[:NAME_MAX] + "-*") if p.is_dir())


def when(ts):
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def calls_and_compactions(path, since):
    """The main loop's API calls (one per message id) and the compactions, in file order."""
    calls, compactions, seen = [], [], set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "compact_boundary" not in line and '"assistant"' not in line:
                continue                        # cheap skip; the parsed entry decides
            e = json.loads(line)
            if e.get("subtype") == "compact_boundary":
                if when(e["timestamp"]) >= since:
                    m = e.get("compactMetadata", {})
                    compactions.append((when(e["timestamp"]), m.get("trigger", "?"), m.get("preTokens", 0)))
                continue
            if e.get("type") != "assistant" or e.get("isSidechain"):
                continue
            msg = e.get("message", {})
            mid, usage = msg.get("id"), msg.get("usage") or {}
            if mid in seen or not usage:
                continue
            seen.add(mid)
            calls.append((when(e["timestamp"]), usage.get("cache_read_input_tokens", 0),
                          usage.get("cache_creation_input_tokens", 0)))
    return calls, compactions


def main():
    ap = argparse.ArgumentParser(description="Prompt-cache report from a home's Claude Code transcripts.")
    ap.add_argument("--home", default=".", help="the folder the sessions start in (default: the current folder)")
    ap.add_argument("--hours", type=float, default=24, help="the window, in hours (default 24)")
    ap.add_argument("--log", metavar="FILE", help="append one tab-separated row per run to FILE")
    a = ap.parse_args()
    wanted, dirs = transcript_dirs(a.home)
    if not dirs:
        print(f"cache-report: no transcripts for {os.path.abspath(a.home)} (looked for {wanted})",
              file=sys.stderr)
        return 1
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(hours=a.hours)
    pings, colds, compactions, peak, read_any = [], [], [], 0, False
    for path in sorted(p for d in dirs for p in d.glob("*.jsonl")):
        if dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc) < since:
            continue
        read_any = True
        calls, comps = calls_and_compactions(path, since)
        compactions += comps
        prev = None
        for t, read, write in calls:
            gap = (t - prev).total_seconds() / 60 if prev else None
            prev = t
            if t < since:
                continue
            peak = max(peak, read + write)
            if gap is not None and gap >= PING_GAP_MIN and write <= COLD_WRITE:
                pings.append((t, gap, read, write))
            if write > COLD_WRITE:
                colds.append((t, gap, write))
    if not read_any:                    # zeros here would read as a quiet day (kit #72)
        print(f"cache-report: no transcript in {', '.join(map(str, dirs))} was written in the last "
              f"{a.hours:g} h", file=sys.stderr)
        return 1

    def local(t):
        return t.astimezone().strftime("%d.%m %H:%M")

    ping_read = sum(p[2] for p in pings)
    cold_write = sum(c[2] for c in colds)
    print(f"Prompt cache, last {a.hours:g} h (since {local(since)}), from {', '.join(map(str, dirs))}")
    gaps = [p[1] for p in pings]
    print(f"- idle pings: {len(pings)}" + (f", gaps {min(gaps):.0f}-{max(gaps):.0f} min, "
                                          f"{ping_read/1e6:.1f}M tokens read from cache" if pings else ""))
    if colds:
        for t, gap, write in colds:
            print(f"- cold rebuild {local(t)}: {write/1000:.0f}k written"
                  + (f" after {gap:.0f} min idle" if gap is not None else " (new session)"))
    else:
        print("- cold rebuilds: none")
    print(f"- compactions: {len(compactions)}"
          + "".join(f"; {local(t)} {trig} at {pre/1000:.0f}k" for t, trig, pre in compactions))
    print(f"- largest context: {peak/1000:.0f}k")
    print(f"- cost [assumed rates]: pings {ping_read*READ_RATE/1e6:.2f}M, "
          f"cold rebuilds {cold_write*WRITE_RATE/1e6:.2f}M base-input tokens")
    if a.log:
        log = pathlib.Path(a.log)
        new = not log.exists()
        with open(log, "a", encoding="utf-8", newline="\n") as f:
            if new:
                f.write("date\thours\tpings\tping_read\tcold_rebuilds\tcold_write\tcompactions\tpeak_context\n")
            f.write(f"{now.astimezone().strftime('%Y-%m-%d %H:%M')}\t{a.hours:g}\t{len(pings)}\t{ping_read}\t"
                    f"{len(colds)}\t{cold_write}\t{len(compactions)}\t{peak}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
