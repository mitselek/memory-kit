#!/usr/bin/env python3
"""Generate schemas/*.json from caps.yaml.

One source for every cap. Never hand-edit the generated files: regenerating must
produce no diff, and the lint's fixture run checks exactly that.

Usage:  python3 tools/gen-schemas.py          write schemas/
        python3 tools/gen-schemas.py --check  exit 1 if regenerating would change anything
"""
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    sys.exit("memory-kit: PyYAML is required.  apt install python3-yaml  |  pip install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPS = yaml.safe_load((ROOT / "caps.yaml").read_text())
REF = CAPS["ref_grammar"]["pattern"]
DRAFT = "https://json-schema.org/draft/2020-12/schema"

HEADER = "GENERATED from caps.yaml by tools/gen-schemas.py. Do not hand-edit."


def ref_field(desc):
    return {"type": "string", "pattern": REF, "description": desc}


def schemas():
    c = CAPS
    record = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label", "record", "ref"],
        "properties": {
            "label": {"enum": ["DECISION", "LEARNED", "WARNING", "WIP",
                               "DEFERRED", "PATTERN", "GOTCHA"]},
            "record": {"type": "string", "maxLength": c["scratchpad"]["record_chars"],
                       "description": "One idea. Does not fit? It is two records. No URLs."},
            "ref": ref_field("Origin. Blank is counted, never failed."),
        },
    }

    fact = {
        "type": "object",
        "additionalProperties": False,
        "required": ["fact", "ref", "refute", "verified"],
        "properties": {
            "fact": {"type": "string",
                     "description": f"One sentence, present tense, <= {c['facts']['fact_words']} words."},
            "ref": ref_field("Origin of the claim."),
            "refute": {"type": "string",
                       "description": "Where to prove this WRONG: a command or a path. "
                                      "'=ref' when the origin doubles as the test. "
                                      "Blank = no test known; the lint counts it."},
            "verified": {"type": "string", "format": "date",
                         "description": "Last date this SURVIVED a refutation attempt. Not a birthday."},
        },
    }

    dormant_fact = json.loads(json.dumps(fact))
    dormant_fact["required"] = fact["required"] + ["parked", "reviewed"]
    dormant_fact["properties"]["parked"] = {"type": "string", "description": "Why it is parked."}
    dormant_fact["properties"]["reviewed"] = {
        "type": "string", "description": "How and when to check whether it should return."}

    rule = {
        "type": "object",
        "additionalProperties": False,
        "required": ["rule", "ref"],
        "properties": {
            "rule": {"type": "string", "maxLength": c["rules"]["rule_chars"],
                     "description": "Imperative. Read on every spawn, so keep it short."},
            "ref": ref_field("A ruling or the incident that created it."),
        },
    }

    core_rule = json.loads(json.dumps(rule))
    core_rule["required"] = rule["required"] + ["core", "incident"]
    core_rule["properties"]["core"] = {
        "enum": ["mandatory", "optional"],
        "description": "mandatory = the kit's own operation; optional = hygiene, a home may "
                       "disable it with a recorded reason."}
    core_rule["properties"]["incident"] = {
        "type": "string",
        "description": "The specific, repeated, recorded mistake a home would make without "
                       "this rule. No incident, no core."}

    return {
        "scratchpad": {
            "title": "Scratchpad", "type": "object", "additionalProperties": False,
            "required": ["current", "staging"],
            "properties": {
                "current": {"type": "array", "items": record,
                            "maxItems": c["scratchpad"]["current_rows"],
                            "description": "Act on these next session. Regenerated at close, never appended."},
                "staging": {"type": "array", "items": record,
                            "description": "Do not re-derive these. current + staging <= "
                                           f"{c['scratchpad']['total_rows']} (checked by the lint)."},
            },
        },
        "facts": {
            "title": "Facts file", "type": "object", "additionalProperties": False,
            "required": ["facts"],
            "properties": {"facts": {"type": "array", "items": fact,
                                     "maxItems": c["facts"]["per_file"]}},
        },
        "dormant": {
            "title": "Dormant facts", "type": "object", "additionalProperties": False,
            "required": ["facts"],
            "properties": {"facts": {"type": "array", "items": dormant_fact,
                                     "maxItems": c["dormant"]["per_file"]}},
        },
        "rules": {
            "title": "Rules", "type": "object", "additionalProperties": False,
            "required": ["rules"],
            "properties": {"rules": {"type": "array", "items": rule,
                                     "maxItems": c["rules"]["rows"]}},
        },
        "core-rules": {
            "title": "Core rules (ship with the kit)", "type": "object",
            "additionalProperties": False, "required": ["rules"],
            "properties": {"rules": {"type": "array", "items": core_rule,
                                     "maxItems": c["core"]["rules"]}},
        },
    }


def main():
    check = "--check" in sys.argv
    out = ROOT / "schemas"
    out.mkdir(exist_ok=True)
    drift = []
    for name, body in schemas().items():
        doc = {"$schema": DRAFT,
               "$id": f"https://codeberg.org/mitselek/memory-kit/schemas/{name}.json",
               "$comment": HEADER, **body}
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = out / f"{name}.json"
        if check:
            if not path.exists() or path.read_text() != text:
                drift.append(path.name)
        else:
            path.write_text(text)
    if check:
        if drift:
            print("stale (regenerate): " + ", ".join(drift))
            return 1
        print("schemas current")
        return 0
    print(f"wrote {len(schemas())} schemas from caps.yaml v{CAPS['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
