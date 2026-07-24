"""
presidio_recognizer.py — contextual PII detection via Presidio + spaCy trf.

Single Responsibility: detects PERSON, COMPANY only. ADDRESS is handled
entirely by regex_recognizers.py — spaCy's NER recognizes place names,
not structured multi-line postal addresses, so routing LOCATION through
here was pure noise (0% recall, high false-positive volume). Structured
types (EMAIL/PHONE/SSN/CREDIT_CARD/IP/DOB/ADDRESS) are deliberately NOT
routed through here — see regex_recognizers.py docstring for why.
"""

from typing import List

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from src.models import Match

NLP_CONFIGURATION = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_trf"}],
}

# Suppresses known false positives common in Indian financial/regulatory prose.
WHITELIST = {
    "sebi", "nse", "bse", "rbi", "gst", "pan", "ipo", "roc", "icai",
    "companies act", "ind as", "us gaap", "ifrs", "fema", "scra", "scrr",
    "asba", "qib", "nii", "rii", "ebitda", "cagr", "hufs", "brlm", "brlms",
    "the offer", "fresh issue", "offer for sale", "net proceeds",
    "red herring prospectus", "draft red herring prospectus",
    "llp", "cfo", "ceo", "statutory auditors",
}

# NOTE: "LOCATION": "ADDRESS" removed — see module docstring.
PRESIDIO_LABEL_MAP = {
    "PERSON": "PERSON",
    "ORGANIZATION": "COMPANY",
}

MIN_ORG_TOKENS = 2  # drop single-token ORG hits like "LLP", "OFFER"

_analyzer = None  # lazy-loaded singleton, trf model is slow to load


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is None:
        provider = NlpEngineProvider(nlp_configuration=NLP_CONFIGURATION)
        nlp_engine = provider.create_engine()
        _analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    return _analyzer


def detect(text: str) -> List[Match]:
    analyzer = _get_analyzer()
    results = analyzer.analyze(
        text=text, language="en",
        entities=list(PRESIDIO_LABEL_MAP.keys()),
    )
    matches: List[Match] = []
    for r in results:
        label = PRESIDIO_LABEL_MAP.get(r.entity_type)
        if not label:
            continue
        span_text = text[r.start:r.end]
        if span_text.strip().lower() in WHITELIST:
            continue
        if label == "COMPANY" and len(span_text.split()) < MIN_ORG_TOKENS:
            continue
        matches.append(Match(r.start, r.end, span_text, label, r.score, "presidio", "spacy_trf"))
    return matches