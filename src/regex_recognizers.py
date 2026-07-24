"""
regex_recognizers.py — deterministic detection for structured PII.

Single Responsibility: this file ONLY detects (returns Match objects),
never modifies text. Own regex chosen deliberately over generic NLP
recognizers for EMAIL/PHONE/SSN/CREDIT_CARD/IP/DOB/ADDRESS because these
formats are fully deterministic — a hand-tuned regex is more explainable
and more precise here than a general-purpose model (see README tradeoffs
section).
"""

import re
from typing import List

from src.models import Match


def _luhn_check(number: str) -> bool:
    """Validates a candidate credit-card number to reject generic long
    digit runs (invoice numbers, reference IDs, etc.)."""
    digits = [int(d) for d in re.sub(r"[ -]", "", number)]
    if not (13 <= len(digits) <= 19):
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
)

SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,19}\b")

# UPDATED: allows a space between "+" and "91", allows parens around
# any digit group (not just right after 91), loosens digit grouping to
# 3-5 per chunk instead of a rigid 4-5/4-5 split.
PHONE_PATTERN = re.compile(
    r"(?:\+?\s?91[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}"
    r"|\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)

DOB_PATTERN = re.compile(
    r"(?:born on|date of birth|dob)[:\s]+"
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    re.IGNORECASE,
)

DIN_PATTERN = re.compile(r"\bDIN[:\s]+(\d{8})\b", re.IGNORECASE)

# --- ADDRESS detection ---
ADDRESS_SIGNAL_KEYWORDS = re.compile(
    r"\b(Village|Taluka|Road|Marg|Nagar|Society|Colony|Park|Complex|"
    r"Chambers|Building|Floor|Wing|Estate|Industrial|Lane|Bhavan|House|"
    r"Compound|Tower|Towers|Bapat|Kurla|Gymkhana|Residency|Bunglow|"
    r"Apartment|Plot)\b",
    re.IGNORECASE,
)

PIN_CODE_PATTERN = re.compile(r"\b\d{3}\s?\d{3}\b")


def _detect_addresses(text: str) -> List[Match]:
    matches: List[Match] = []
    for m in PIN_CODE_PATTERN.finditer(text):
        window_start = max(0, m.start() - 200)
        window = text[window_start:m.end()]
        if not ADDRESS_SIGNAL_KEYWORDS.search(window):
            continue
        line_start = text.rfind("\n", window_start, m.start())
        line_start = 0 if line_start == -1 and window_start == 0 else (line_start + 1 if line_start != -1 else window_start)
        span_text = text[line_start:m.end()].strip()
        if len(span_text) < 15:
            continue
        matches.append(Match(line_start, m.end(), span_text, "ADDRESS", 0.8, "regex", "address_pincode_regex"))
    return matches
# --- END ---


# --- Company-suffix detection (catches names spaCy's NER misses,
# e.g. "State Bank of India", "Citibank N.A.", "Kanj and Co LLP") ---
COMPANY_SUFFIX_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z&.,\-]*(?:\s+[A-Z][A-Za-z&.,\-]*){0,6}\s+"
    r"(?:Limited|Ltd\.?|LLP|Bank(?:\s+of\s+India)?|N\.A\.|"
    r"& Associates|& Co\.?|and Co\.?\s*LLP|Bank Limited))\b"
)


def _detect_company_suffixes(text: str) -> List[Match]:
    matches = []
    for m in COMPANY_SUFFIX_PATTERN.finditer(text):
        matches.append(Match(m.start(1), m.end(1), m.group(1), "COMPANY", 0.75, "regex", "company_suffix_regex"))
    return matches


# --- Title-context person detection (catches names spaCy misses when
# they sit near a role/designation keyword, e.g. lowercase table rows) ---
PERSON_TITLE_PATTERN = re.compile(
    r"(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|"
    r"Director|Promoter|Signatory|Chairman|Chairperson|"
    r"Managing Director|Company Secretary|Chief Financial Officer|CFO|CEO)"
    r"\s*[:,]?\s+([A-Z][a-zA-Z.\-]+(?:\s+[A-Z][a-zA-Z.\-]+){1,3})"
)


def _detect_titled_persons(text: str) -> List[Match]:
    matches = []
    for m in PERSON_TITLE_PATTERN.finditer(text):
        matches.append(Match(m.start(1), m.end(1), m.group(1), "PERSON", 0.7, "regex", "person_title_regex"))
    return matches
# --- END ---


def detect(text: str) -> List[Match]:
    """Runs every regex recognizer over `text`, returns all matches found.
    To add a new structured PII type: write one compiled pattern above,
    add one block below. Nothing else in the codebase changes."""
    matches: List[Match] = []

    for m in EMAIL_PATTERN.finditer(text):
        matches.append(Match(m.start(), m.end(), m.group(0), "EMAIL", 1.0, "regex", "email_regex"))

    for m in IP_PATTERN.finditer(text):
        matches.append(Match(m.start(), m.end(), m.group(0), "IP_ADDRESS", 0.95, "regex", "ip_regex"))

    for m in SSN_PATTERN.finditer(text):
        matches.append(Match(m.start(), m.end(), m.group(0), "SSN", 0.95, "regex", "ssn_regex"))

    for m in CREDIT_CARD_PATTERN.finditer(text):
        span_text = m.group(0)
        if _luhn_check(span_text):
            matches.append(Match(m.start(), m.end(), span_text, "CREDIT_CARD", 0.9, "regex", "credit_card_regex_luhn"))

    for m in PHONE_PATTERN.finditer(text):
        span_text = m.group(0)
        if len(re.sub(r"\D", "", span_text)) >= 10:
            matches.append(Match(m.start(), m.end(), span_text, "PHONE", 0.85, "regex", "phone_regex"))

    for m in DOB_PATTERN.finditer(text):
        matches.append(Match(m.start(1), m.end(1), m.group(1), "DATE_OF_BIRTH", 0.9, "regex", "dob_keyword_regex"))

    for m in DIN_PATTERN.finditer(text):
        matches.append(Match(m.start(1), m.end(1), m.group(1), "DIN", 0.9, "regex", "din_regex"))

    matches.extend(_detect_addresses(text))
    matches.extend(_detect_company_suffixes(text))
    matches.extend(_detect_titled_persons(text))

    return matches