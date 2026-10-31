#!/usr/bin/env python3
"""Tests for tools/lesson-index.py's command line (kit #62): stdlib unittest, PyYAML, no network.

    python3 tools/lesson-index-test.py

--help prints usage and writes nothing; an unknown flag is refused; with no folder named the memory
directory comes from memory-kit.conf; a missing one is a one-line error, nothing created.
Each run is a real subprocess in a temporary folder.
"""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TOOL = pathlib.Path(__file__).resolve().parent / "lesson-index.py"
LESSON = '---\nsummary: "A lesson."\nlearned: "2026-10-15"\nref: me:2026-10-15\nenforcement: recognition\n---\n# T\nbody\n'


def run(cwd, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-I", str(TOOL), *args], cwd=cwd, env=env,
                          capture_output=True, text=True, encoding="utf-8")


def tree(root):
    return sorted(str(p.relative_to(root)) for p in pathlib.Path(root).rglob("*"))


class LessonIndexCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def lesson(self, mem):
        d = pathlib.Path(self.cwd) / mem / "lessons"
        d.mkdir(parents=True)
        with open(d / "a.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(LESSON)

    def test_help_prints_usage_and_writes_nothing(self):
        self.lesson("memory")
        before = tree(self.cwd)
        for flag in ("--help", "-h"):
            r = run(self.cwd, flag)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Usage", r.stdout)
            self.assertEqual(tree(self.cwd), before)

    def test_help_without_a_memory_dir_is_still_help(self):
        r = run(self.cwd, "--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Usage", r.stdout)
        self.assertEqual(tree(self.cwd), [])

    def test_unknown_flag_exits_2_with_usage_and_writes_nothing(self):
        self.lesson("memory")
        before = tree(self.cwd)
        r = run(self.cwd, "--bogus")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--bogus", r.stderr)
        self.assertIn("Usage", r.stderr)
        self.assertEqual(tree(self.cwd), before)

    def test_memory_dir_comes_from_the_conf(self):
        self.lesson("mem")
        (pathlib.Path(self.cwd) / "memory-kit.conf").write_text("memory_dir: mem\n", encoding="utf-8")
        r = run(self.cwd)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("a", (pathlib.Path(self.cwd) / "mem/lessons/index.yaml").read_text(encoding="utf-8"))
        self.assertFalse((pathlib.Path(self.cwd) / "memory").exists())

    def test_conf_is_found_from_a_subfolder(self):
        self.lesson("mem")
        (pathlib.Path(self.cwd) / "memory-kit.conf").write_text("memory_dir: mem\n", encoding="utf-8")
        sub = pathlib.Path(self.cwd) / "proj"
        sub.mkdir()
        r = run(sub)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((pathlib.Path(self.cwd) / "mem/lessons/index.yaml").exists())

    def test_no_conf_defaults_to_memory(self):
        self.lesson("memory")
        r = run(self.cwd)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((pathlib.Path(self.cwd) / "memory/lessons/index.yaml").exists())

    def test_named_dir_is_taken_as_given(self):
        self.lesson("elsewhere")
        r = run(self.cwd, "elsewhere")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((pathlib.Path(self.cwd) / "elsewhere/lessons/index.yaml").exists())

    def test_missing_memory_dir_is_one_line_and_creates_nothing(self):
        for args in ((), ("nowhere",)):
            r = run(self.cwd, *args)
            self.assertEqual(r.returncode, 1)
            self.assertNotIn("Traceback", r.stderr)
            self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
            self.assertEqual(tree(self.cwd), [])

    def test_check_with_a_missing_lessons_dir_creates_nothing(self):
        (pathlib.Path(self.cwd) / "memory").mkdir()
        r = run(self.cwd, "--check")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(tree(self.cwd), ["memory"])


if __name__ == "__main__":
    unittest.main()
