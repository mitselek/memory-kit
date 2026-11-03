#!/usr/bin/env python3
"""Tests for adapters/claude-code/tools/cache-report.py (kit #70): stdlib unittest, no network.

    python3 adapters/claude-code/tools/cache-report-test.py

Each run is a real subprocess (python3 -I) with HOME pointed at a temporary folder holding one
small fixture transcript, so the tool finds it exactly where Claude Code would put it.
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TOOL = pathlib.Path(__file__).resolve().parent / "cache-report.py"
NOW = dt.datetime.now(dt.timezone.utc)


def ts(minutes_ago):
    return (NOW - dt.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def assistant(minutes_ago, mid, read, write, sidechain=False, text="ok"):
    return {"type": "assistant", "isSidechain": sidechain, "timestamp": ts(minutes_ago),
            "message": {"id": mid, "content": [{"type": "text", "text": text}], "usage": {"input_tokens": 3, "output_tokens": 50,
                                             "cache_read_input_tokens": read,
                                             "cache_creation_input_tokens": write}}}


# A session that started 180 minutes ago: a cold start; one warm call whose text names
# compact_boundary (still a call, not a compaction); one idle ping after 50 minutes; the same
# message again (one API call, two transcript lines); a subagent's call; a compaction; and a cold
# rebuild after 65 minutes idle.
FIXTURE = [
    {"type": "user", "timestamp": ts(181), "message": {"role": "user", "content": "hello"}},
    assistant(180, "msg_1", 0, 80_000),
    assistant(175, "msg_2", 80_000, 2_000, text='a "compact_boundary" line marks a compaction'),
    assistant(125, "msg_3", 82_000, 1_000),
    assistant(125, "msg_3", 82_000, 1_000),
    assistant(124, "msg_side", 0, 300_000, sidechain=True),
    {"type": "system", "subtype": "compact_boundary", "timestamp": ts(70),
     "compactMetadata": {"trigger": "auto", "preTokens": 250_000}},
    assistant(60, "msg_4", 0, 90_000),
]


def folder_name(path):
    """Claude Code's rule, written out independently of the tool."""
    return re.sub(r"[^a-zA-Z0-9]", "-", str(path))


def tree(root):
    return sorted(str(p.relative_to(root)) for p in pathlib.Path(root).rglob("*"))


class CacheReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.home = self.root / "my home.v2"          # a space and a dot: both become "-"
        self.home.mkdir()
        self.transcripts = self.root / ".claude" / "projects" / folder_name(self.home)
        self.transcripts.mkdir(parents=True)
        with open(self.transcripts / "session.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for e in FIXTURE:
                f.write(json.dumps(e, separators=(",", ":")) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args, cwd=None):
        env = dict(os.environ, HOME=str(self.root), PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-I", str(TOOL), *args], cwd=cwd or self.home,
                              env=env, capture_output=True, text=True, encoding="utf-8")

    def test_report_from_the_session_folder(self):
        r = self.run_tool()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn("- idle pings: 1, gaps 50-50 min, 0.1M tokens read from cache", out)
        self.assertRegex(out, r"- cold rebuild .*: 80k written \(new session\)")
        self.assertRegex(out, r"- cold rebuild .*: 90k written after 65 min idle")
        self.assertRegex(out, r"- compactions: 1; .* auto at 250k")
        self.assertIn("- largest context: 90k", out)
        self.assertIn("pings 0.01M, cold rebuilds 0.34M base-input tokens", out)
        self.assertNotIn("300k", out)               # the subagent's call is not the main loop

    def test_home_named_on_the_command_line(self):
        r = self.run_tool("--home", str(self.home), cwd=self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("idle pings: 1", r.stdout)

    def test_window_excludes_older_calls(self):
        r = self.run_tool("--hours", "1.5")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("- idle pings: 0", r.stdout)
        self.assertNotIn("80k written", r.stdout)
        self.assertIn("90k written after 65 min idle", r.stdout)

    def test_log_appends_one_row_per_run(self):
        log = self.root / "logs" / "cache.tsv"
        log.parent.mkdir()
        for _ in range(2):
            r = self.run_tool("--log", str(log))
            self.assertEqual(r.returncode, 0, r.stderr)
        with open(log, encoding="utf-8") as f:
            rows = f.read().splitlines()
        self.assertEqual(rows[0].split("\t"), ["date", "hours", "pings", "ping_read", "cold_rebuilds",
                                               "cold_write", "compactions", "peak_context"])
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1].split("\t")[2:], ["1", "82000", "2", "170000", "1", "90000"])

    def test_no_transcripts_is_a_one_line_error(self):
        other = self.root / "elsewhere"
        other.mkdir()
        before = tree(self.root)
        r = self.run_tool(cwd=other)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")
        self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
        self.assertIn(folder_name(other), r.stderr)
        self.assertEqual(tree(self.root), before)

    def test_help_writes_nothing(self):
        before = tree(self.root)
        r = self.run_tool("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--log", r.stdout)
        self.assertEqual(tree(self.root), before)

    def test_unknown_flag_is_refused(self):
        r = self.run_tool("--nope")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
