#!/usr/bin/env python3
"""Tests for tools/kit-update.py: the stdlib alone (unittest), no network, no git.

    python3 tools/kit-update-test.py

git and the lint run through subprocess.run, which a fake replaces: it answers each command the
tool runs from a small table and records what it was given. Ultrareview of main at
v0.1.0-alpha.13, findings 1, 4 and 5.
"""
import importlib.util
import io
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

# Loading kit-update.py must leave nothing behind in tools/ (no __pycache__).
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("kit_update", HERE / "kit-update.py")
ku = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ku)

UPGRADE = """## Per version
- **0.1.0-alpha.11 -> 0.1.0-alpha.12:** no data step. Pull, lint.
- **0.1.0-alpha.12 -> 0.1.0-alpha.13:** no data step. Pull, lint.
- **0.1.0-alpha.13 -> 0.1.0-alpha.14:** no data step. Pull, lint.
"""


class FakeHost:
    """subprocess.run for the tool: git and the lint answered from a table, every call recorded."""

    def __init__(self, tags, upgrade=UPGRADE, pull="ok", reset_rc=0, fetch="ok"):
        self.tags, self.upgrade, self.pull, self.reset_rc, self.fetch = tags, upgrade, pull, reset_rc, fetch
        self.calls = []

    def __call__(self, argv, **kw):
        self.calls.append((list(argv), kw))
        done = lambda rc=0, out="", err="": subprocess.CompletedProcess(argv, rc, out, err)
        words = [a for a in argv if not a.startswith("-") and a != "git"]
        if "ls-remote" in argv:
            return done(out="".join(f"abc\trefs/tags/{t}\n" for t in self.tags))
        if argv[0] == "bash":
            return done()  # the lint gate passes
        cmd = argv[3] if argv[:2] == ["git", "-C"] else words[0]
        if cmd == "status":
            return done()
        if cmd == "fetch":
            if self.fetch == "hang":
                raise subprocess.TimeoutExpired(argv, kw.get("timeout"))
            return done()
        if cmd == "show":
            return done(out=self.upgrade)
        if cmd == "rev-parse":
            return done(out="start123\n")
        if cmd == "subtree":
            if self.pull == "hang":
                raise subprocess.TimeoutExpired(argv, kw.get("timeout"))
            return done(rc=0 if self.pull == "ok" else 1, err="" if self.pull == "ok" else "conflict")
        if cmd == "reset":
            return done(rc=self.reset_rc, err="" if self.reset_rc == 0 else "fatal: Unable to create '.git/index.lock': File exists.")
        if cmd == "diff":
            return done()
        raise AssertionError(f"unexpected command: {argv}")

    def timeout_of(self, cmd):
        return [kw.get("timeout") for argv, kw in self.calls if argv[:2] == ["git", "-C"] and argv[3] == cmd]


def run_tool(host, current="0.1.0-alpha.13", channel="latest"):
    with tempfile.TemporaryDirectory() as d:
        home = pathlib.Path(d)
        (home / "memory-kit").mkdir()
        (home / "memory-kit" / "VERSION").write_text(current + "\n", encoding="utf-8")
        (home / "memory-kit.conf").write_text(f"update: {channel}\n", encoding="utf-8")
        real, ku.subprocess.run = ku.subprocess.run, host
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                code = ku.main(["kit-update.py", str(home)])
        finally:
            ku.subprocess.run = real
        return code, out.getvalue()


class Finding1CurrentVersionAlwaysOnThePath(unittest.TestCase):
    def test_the_path_starts_at_the_current_version_even_when_its_tag_is_gone(self):
        releases = ["v0.1.0-alpha.12", "v0.1.0-alpha.14"]  # v0.1.0-alpha.13 deleted upstream
        self.assertEqual(ku.step_path("0.1.0-alpha.13", releases, "v0.1.0-alpha.14"), ["0.1.0-alpha.13", "0.1.0-alpha.14"])
        self.assertEqual(
            ku.step_path("0.1.0-alpha.12", ["v0.1.0-alpha.12", "v0.1.0-alpha.13", "v0.1.0-alpha.14"], "v0.1.0-alpha.14"),
            ["0.1.0-alpha.12", "0.1.0-alpha.13", "0.1.0-alpha.14"],
        )

    def test_a_missing_entry_for_the_current_hop_refuses(self):
        md = "- **0.1.0-alpha.12 -> 0.1.0-alpha.14:** no data step.\n"
        path = ku.step_path("0.1.0-alpha.13", ["v0.1.0-alpha.12", "v0.1.0-alpha.14"], "v0.1.0-alpha.14")
        self.assertEqual(ku.data_steps_ok(md, path), "UPGRADE.md has no entry for 0.1.0-alpha.13 -> 0.1.0-alpha.14")

    def test_end_to_end_a_gone_current_tag_and_no_entry_is_refused_before_any_pull(self):
        host = FakeHost(tags=["v0.1.0-alpha.12", "v0.1.0-alpha.14"], upgrade="- **0.1.0-alpha.12 -> 0.1.0-alpha.14:** no data step.\n")
        code, out = run_tool(host)
        self.assertEqual(code, 1)
        self.assertIn("refused: UPGRADE.md has no entry for 0.1.0-alpha.13 -> 0.1.0-alpha.14", out)
        self.assertEqual(host.timeout_of("subtree"), [])


class Finding4ARollbackThatFailsIsSaidPlainly(unittest.TestCase):
    def test_a_failed_pull_whose_reset_works_is_undone_exit_1(self):
        code, out = run_tool(FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"], pull="fail"))
        self.assertEqual(code, 1)
        self.assertIn("subtree pull failed: conflict; the pull is undone (back to start123)", out)

    def test_a_failed_pull_whose_reset_fails_says_so_and_exits_3(self):
        code, out = run_tool(FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"], pull="fail", reset_rc=128))
        self.assertEqual(code, ku.EXIT_ROLLBACK_FAILED)
        self.assertEqual(ku.EXIT_ROLLBACK_FAILED, 3)
        self.assertNotIn("undone:", out)
        self.assertIn("may be partly pulled", out)
        self.assertIn("git reset --hard start123", out)
        self.assertIn("index.lock", out)


class Finding5NetworkCallsAreBounded(unittest.TestCase):
    def test_fetch_and_subtree_pull_carry_the_timeout(self):
        host = FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"])
        code, out = run_tool(host)
        self.assertEqual(code, 0, out)
        self.assertEqual(host.timeout_of("fetch"), [ku.NETWORK_TIMEOUT])
        self.assertEqual(host.timeout_of("subtree"), [ku.NETWORK_TIMEOUT])
        self.assertEqual(ku.NETWORK_TIMEOUT, 300)

    def test_a_pull_that_times_out_is_a_failure_and_rolled_back(self):
        host = FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"], pull="hang")
        code, out = run_tool(host)
        self.assertEqual(code, 1)
        self.assertIn("timed out after 300 s", out)
        self.assertEqual(len(host.timeout_of("reset")), 1)

    def test_a_fetch_that_times_out_fails_cleanly_before_anything_changed(self):
        host = FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"], fetch="hang")
        code, out = run_tool(host)
        self.assertEqual(code, 1)
        self.assertIn("timed out after 300 s", out)
        self.assertEqual(host.timeout_of("subtree"), [])

    def test_git_never_waits_on_a_credential_prompt(self):
        host = FakeHost(tags=["v0.1.0-alpha.13", "v0.1.0-alpha.14"])
        run_tool(host)
        fetch_env = [kw.get("env") or {} for argv, kw in host.calls if "fetch" in argv][0]
        self.assertEqual(fetch_env.get("GIT_TERMINAL_PROMPT"), "0")


if __name__ == "__main__":
    unittest.main(verbosity=1)
