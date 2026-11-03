#!/usr/bin/env python3
"""Find text that narrates a document's own history instead of stating what is.

    python3 scan.py FILE [FILE ...]          candidate lines, one per hit
    python3 scan.py --ids FILE [FILE ...]    also: ids used only once across the files
    python3 scan.py --help                   this text

Prints `file:line: [category] match | context`. Every hit is a candidate for a human
(or the state-what-is skill) to judge; none is a verdict. HTML tags are stripped before
matching, line numbers are kept. English and Estonian. Stdlib only.
"""
import re
import sys
from collections import Counter

CATEGORIES = [
    ("narration", re.compile(
        r"\b(no longer|any ?more|after all|this (reverses|replaces|supersedes|overturns)"
        r"|reverses|replaced by|superseded by|was (dropped|removed|added|renamed|withdrawn)"
        r"|we (dropped|removed|changed|decided|reversed)|originally|previously|initially"
        r"|at first|used to|turned out|on second thought|not adopted|earlier (draft|version|idea|proposal)"
        r"|now (is|are|does|uses|says|has|lists|carries|reads|makes|stamps|owns))\b", re.I)),
    ("narration-et", re.compile(
        r"\b(enam (ei|pole|mitte)|(ei|pole) (\w+ ){0,2}enam|varem|algselt|esialgu"
        r"|nüüd (on|ei|pole|käib|tähendab|kasutab|saab)|eelmise(s|st)? versiooni(s|st)?"
        r"|loobusime|loobuti|jäeti välja|asendati|asendatud|tühistati|kaotati|pärast kõike"
        r"|muutsime|muudeti)\b", re.I)),
    ("version-in-body", re.compile(r"\bv\d+\.\d+\b[^.]{0,40}\b(adds?|added|makes?|made|drops?|dropped|fix(es|ed)?)\b", re.I)),
    ("absence", re.compile(r"\b(isn't|is not|aren't|doesn't|does not|has no|there is no|there's no|without)\b[^.]{0,60}", re.I)),
]
ID = re.compile(r"\b([A-Z]{1,3}\d{1,3}[a-z]?)\b")
JIRA = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d{1,6})\b")
NOT_JIRA = {"UTF", "SHA", "ISO", "EN", "RFC", "IEC", "IEEE", "TLS", "HTTP", "MD", "X"}
TAG = re.compile(r"<[^>]+>")
HTML_LINK = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S | re.I)
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def lines_of(path, raw):
    text = raw
    if path.lower().endswith((".html", ".htm")):
        text = re.sub(r"<(style|script)\b.*?</\1>", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S | re.I)
        text = TAG.sub(" ", text)
    return text.split("\n")


def linked_keys(path, raw):
    """Jira keys a reader can follow: inside a link's text or target, or in a URL."""
    found = set()
    links = HTML_LINK.findall(raw) if path.lower().endswith((".html", ".htm")) else MD_LINK.findall(raw)
    for a, b in links:
        found.update(JIRA.findall(a + " " + b))
    found.update(re.findall(r"/browse/([A-Z][A-Z0-9]{1,9}-\d{1,6})", raw))
    return found


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    bad = [a for a in argv if a.startswith("-") and a != "--ids"]
    if bad:
        print(f"scan.py: unknown option {bad[0]}; see --help", file=sys.stderr)
        return 2
    ids = "--ids" in argv
    files = [a for a in argv if a != "--ids"]
    if not files:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    texts = []
    for path in files:                  # every file read before any hit is printed
        try:
            texts.append((path, read(path)))
        except (OSError, UnicodeDecodeError) as e:
            print(f"scan.py: cannot read {path}: {getattr(e, 'strerror', None) or e}", file=sys.stderr)
            return 2
    counts = Counter()
    first = {}
    hits = 0
    for path, raw in texts:
        linked = linked_keys(path, raw)
        reported = set()
        for n, line in enumerate(lines_of(path, raw), 1):
            for name, rx in CATEGORIES:
                for m in rx.finditer(line):
                    hits += 1
                    ctx = line.strip()
                    if len(ctx) > 140:
                        start = max(0, m.start() - 50)
                        ctx = "…" + line[start:start + 140].strip() + "…"
                    print(f"{path}:{n}: [{name}] {m.group(0)!r} | {ctx}")
            for m in JIRA.finditer(line):
                key = m.group(1)
                if key.split("-")[0] in NOT_JIRA or key in linked or key in reported:
                    continue
                reported.add(key)
                hits += 1
                print(f"{path}:{n}: [unlinked-key] {key!r} | never linked in this file; can the reader follow it?")
            if ids:
                for m in ID.finditer(line):
                    counts[m.group(1)] += 1
                    first.setdefault(m.group(1), f"{path}:{n}")
    if ids:
        for token, c in sorted(counts.items()):
            if c == 1:
                hits += 1
                print(f"{first[token]}: [single-use id] {token!r} | defined anywhere the reader can see?")
    print(f"-- {hits} candidate(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
