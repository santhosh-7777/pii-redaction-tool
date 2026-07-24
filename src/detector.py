"""
detector.py — single entry point: detect(text) -> List[Match].
Calls regex + presidio, merges, resolves overlaps, filters out generic
non-PII boilerplate terms. Nothing outside this file needs to know how
detection works internally.
"""

import re
from typing import List

from src.models import Match
from src.regex_recognizers import detect as regex_detect
from src.presidio_recognizer import detect as presidio_detect


# Generic legal/document boilerplate that presidio's NER mistakes for
# COMPANY/PERSON. Keys are normalized (lowercased, whitespace-collapsed).
_GENERIC_TERMS = {
    "board of directors", "red herring prospectus", "this red herring prospectus",
    "government of india", "ipo committee", "stock exchanges",
    "the stock exchanges for the offer", "european union", "indian gaap",
    "ind as", "care report", "the care report", "careedge research",
    "promoter group", "the promoter", "united states", "registrar of companies",
    "the registrar of companies",
}

# Single-word junk that presidio repeatedly mistags as PERSON — financial/
# document vocabulary and government scheme acronyms, identified from
# actual replacement_log.json output (terms that repeat 5-20+ times as a
# bare single token, which real names in this document type never do).
_GENERIC_SINGLE_WORDS = {
    "the", "and", "offer", "data", "fiscal", "march", "account", "agent",
    "escrow", "bidder", "price", "independent", "branch", "return", "worth",
    "loan", "grill", "million", "metric", "first", "fresh", "last",
    "nach", "pmay", "kusum", "adas", "amrut", "bess", "ddugjy", "emis",
    "gndi", "iebr", "nemmp",
}


def _is_generic_term(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if normalized in _GENERIC_TERMS:
        return True
    if len(normalized) <= 3:
        return True
    # catches integers AND decimals like "384.01", "12167.69" (isdigit()
    # alone misses decimals since "." isn't a digit character)
    if re.fullmatch(r"\d+(\.\d+)?", normalized):
        return True
    if normalized in _GENERIC_SINGLE_WORDS:
        return True
    for term in _GENERIC_TERMS:
        if term in normalized or normalized in term:
            return True
    return False


def _resolve_overlaps(matches: List[Match]) -> List[Match]:
    # Higher confidence wins; regex confidences are set higher than
    # presidio's, so regex wins ties on the same span.
    matches = sorted(matches, key=lambda m: -m.confidence)
    resolved: List[Match] = []
    for m in matches:
        if any(not (m.end <= r.start or m.start >= r.end) for r in resolved):
            continue
        resolved.append(m)
    return sorted(resolved, key=lambda m: m.start)


def detect(text: str) -> List[Match]:
    matches = regex_detect(text) + presidio_detect(text)
    matches = [m for m in matches if not _is_generic_term(m.text)]
    return _resolve_overlaps(matches)