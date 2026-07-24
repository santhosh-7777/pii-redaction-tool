"""
main.py — entry point. Load document, redact, save, done.
"""

from src.redact_docx import redact_docx
import json
from pathlib import Path

if __name__ == "__main__":
    log = redact_docx("input/Red Herring Prospectus.docx", "output/redacted_rhp.docx")
    Path("output/replacement_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Redacted {len(log)} PII instances.")
    print("Saved: output/redacted_rhp.docx")
    print("Saved: output/replacement_log.json")