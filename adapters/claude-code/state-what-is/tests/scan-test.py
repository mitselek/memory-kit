#!/usr/bin/env python3
"""Tests for skills/state-what-is/scan.py (kit #73): stdlib unittest, no network.

    python3 adapters/claude-code/state-what-is/tests/scan-test.py

Each run is a real subprocess (python3 -I) over small files in a temporary folder.
"""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCAN = pathlib.Path(__file__).resolve().parent.parent / "skills" / "state-what-is" / "scan.py"


def tree(root):
    return sorted(str(p.relative_to(root)) for p in pathlib.Path(root).rglob("*"))


class Scan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, name, text):
        path = self.dir / name
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return str(path)

    def run_scan(self, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-I", str(SCAN), *args], cwd=self.dir, env=env,
                              capture_output=True, text=True, encoding="utf-8")

    def test_english_narration_is_a_candidate_with_its_line(self):
        f = self.file("a.md", "# Mail\n\nA maintenance window no longer stops mail.\n")
        r = self.run_scan(f)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"{f}:3: [narration] 'no longer'", r.stdout)

    def test_estonian_narration_is_a_candidate(self):
        f = self.file("et.md", "Seda välja enam ei kasutata.\nAlgselt oli kaks kanalit.\n")
        r = self.run_scan(f)
        self.assertIn(f"{f}:1: [narration-et] 'enam ei'", r.stdout)
        self.assertIn(f"{f}:2: [narration-et] 'Algselt'", r.stdout)

    def test_a_jira_key_is_flagged_until_linked(self):
        f = self.file("j.md", "See VEO-234 for the plan.\n")
        r = self.run_scan(f)
        self.assertIn("[unlinked-key] 'VEO-234'", r.stdout)
        f = self.file("k.md", "See VEO-234 for the plan.\n\n[VEO-234](https://jira.example/browse/VEO-234)\n")
        r = self.run_scan(f)
        self.assertNotIn("unlinked-key", r.stdout)

    def test_ids_used_once_only_with_ids(self):
        f = self.file("i.md", "Vector K28 is out. Q7 and Q7 stay.\n")
        r = self.run_scan(f)
        self.assertNotIn("single-use id", r.stdout)
        r = self.run_scan("--ids", f)
        self.assertIn("[single-use id] 'K28'", r.stdout)
        self.assertNotIn("'Q7'", r.stdout)

    def test_html_tags_are_stripped_and_lines_kept(self):
        f = self.file("p.html", "<html>\n<style>\n.no-longer { }\n</style>\n<p>It <b>no longer</b> waits.</p>\n</html>\n")
        r = self.run_scan(f)
        self.assertIn(f"{f}:5: [narration] 'no longer'", r.stdout)
        self.assertNotIn(f"{f}:3:", r.stdout)

    def test_a_text_that_states_what_is_has_no_candidates(self):
        f = self.file("ok.md", "A maintenance window lets mail through.\n")
        r = self.run_scan(f)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "")
        self.assertIn("-- 0 candidate(s)", r.stderr)

    def test_help_prints_usage_and_writes_nothing(self):
        before = tree(self.dir)
        for flag in ("--help", "-h"):
            r = self.run_scan(flag)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("--ids", r.stdout)
        self.assertEqual(tree(self.dir), before)

    def test_no_file_or_an_unknown_flag_is_refused(self):
        r = self.run_scan()
        self.assertEqual(r.returncode, 2)
        f = self.file("a.md", "text\n")
        r = self.run_scan("--idz", f)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--idz", r.stderr)

    def test_a_missing_file_is_a_one_line_error(self):
        r = self.run_scan(str(self.dir / "gone.md"))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
        self.assertIn("gone.md", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
