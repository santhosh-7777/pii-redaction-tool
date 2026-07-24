"""
redactor.py — applies detected Match[] to plain text, using FakeMapper
for replacement values. Returns redacted text + a log of what changed.
"""

from typing import List, Tuple
from src.models import Match
from src.fake_mapper import FakeMapper


def redact(text: str, matches: List[Match], mapper: FakeMapper) -> Tuple[str, List[dict]]:
    out = []
    cursor = 0
    log = []
    for m in sorted(matches, key=lambda m: m.start):
        out.append(text[cursor:m.start])
        fake = mapper.get(m.text, m.label)
        out.append(fake)
        log.append({
            "type": m.label, "original": m.text, "replacement": fake,
            "confidence": m.confidence, "source": m.source, "rule": m.rule_name,
        })
        cursor = m.end
    out.append(text[cursor:])
    return "".join(out), log