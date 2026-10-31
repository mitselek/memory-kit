#!/usr/bin/env python3
"""The caps the skeleton READMEs state must be the caps in caps.yaml (kit #65).

    python3 tools/caps-docs-test.py

A README line that cites a cap writes it as `NUMBER ... (`tier.key`)`, for example
"at most 120 characters (`lessons.index_line_chars`)". The first number on that line must equal
caps.yaml's value for that key. Every skeleton tier README (facts, dormant, lessons) must also say
"source: caps.yaml", and skeleton/memory/README.md must cite the scratchpad, rules and obligations
caps, which have no README of their own. Stdlib and PyYAML.
"""
import pathlib
import re
import sys
import unittest

import yaml

sys.dont_write_bytecode = True
KIT = pathlib.Path(__file__).resolve().parent.parent
CAPS = yaml.safe_load((KIT / "caps.yaml").read_text(encoding="utf-8"))
CITE = re.compile(r"`([a-z_]+)\.([a-z_]+)`")
SKELETON = KIT / "skeleton" / "memory"


def cited(path):
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in CITE.finditer(line):
            if m.group(1) in CAPS and isinstance(CAPS[m.group(1)], dict) and m.group(2) in CAPS[m.group(1)]:
                num = re.search(r"\b(\d+)\b", line)
                out.append((n, f"{m.group(1)}.{m.group(2)}", int(num.group(1)) if num else None))
    return out


class SkeletonCaps(unittest.TestCase):
    def test_every_cited_cap_matches_caps_yaml(self):
        for p in SKELETON.rglob("README.md"):
            for n, key, num in cited(p):
                tier, name = key.split(".")
                self.assertEqual(num, CAPS[tier][name], f"{p.relative_to(KIT)}:{n} {key}")

    def test_tier_readmes_state_their_caps_and_source(self):
        want = {"facts": ["facts.per_file", "facts.fact_words"], "dormant": ["dormant.per_file"],
                "lessons": ["lessons.index_line_chars"],
                "": ["scratchpad.current_rows", "scratchpad.total_rows", "scratchpad.record_chars",
                     "rules.rows", "rules.rule_chars", "obligations.obligation_chars"]}
        for tier, keys in want.items():
            p = SKELETON / tier / "README.md"
            text = p.read_text(encoding="utf-8")
            self.assertIn("source: caps.yaml", text, str(p.relative_to(KIT)))
            have = {key for _, key, _ in cited(p)}
            self.assertLessEqual(set(keys), have, f"{p.relative_to(KIT)} misses {set(keys) - have}")


if __name__ == "__main__":
    unittest.main()
