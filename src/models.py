"""
models.py — single source of truth for the Match data structure.
Follows Single Responsibility Principle: this file ONLY defines data shape,
zero detection logic, so every other module (regex/presidio/detector/redactor)
can depend on it without circular imports — scalable to any future PII type.
"""

from dataclasses import dataclass


@dataclass
class Match:
    start: int
    end: int
    text: str
    label: str          # e.g. "EMAIL", "PERSON", "PHONE"
    confidence: float    # 0.0-1.0
    source: str          # "regex" or "presidio"
    rule_name: str       # e.g. "email_regex", "spacy_trf_person"