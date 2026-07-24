"""
evaluate.py — compares replacement_log.json (what the code actually
redacted) against ground_truth.json (hand-verified real PII) to compute
real precision/recall/F1 per PII type. No fabricated numbers.

Run from project root:
    python eval/evaluate.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _address_match(pred_text: str, gold_text: str) -> bool:
    """Addresses are multi-line, reformatted by docx run-joining, and gold
    entries may include trailing context (', Maharashtra, India') not
    present on the same physical line as the PIN code. Exact match is
    unrealistic here, so treat it as a match if the gold address's core
    identifying text (with trailing state/country stripped) is contained
    within the predicted span, or vice versa."""
    pred_norm = _normalize(pred_text)
    gold_norm = _normalize(gold_text)
    if pred_norm == gold_norm:
        return True
    gold_core = re.sub(r",?\s*(maharashtra|india)\s*$", "", gold_norm).strip().rstrip(",").strip()
    return gold_core in pred_norm or pred_norm in gold_norm


def evaluate(ground_truth_path: str, log_path: str) -> dict:
    ground_truth = load_json(ground_truth_path)
    predictions = load_json(log_path)

    predicted_set = {(_normalize(p["original"]), p["type"]) for p in predictions}
    gold_set = {(_normalize(g["text"]), g["label"]) for g in ground_truth}

    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for text, label in gold_set:
        if label == "ADDRESS":
            matched = any(
                p_label == label and _address_match(p_text, text)
                for p_text, p_label in predicted_set
            )
        else:
            matched = (text, label) in predicted_set
        if matched:
            stats[label]["tp"] += 1
        else:
            stats[label]["fn"] += 1

    for text, label in predicted_set:
        if label == "ADDRESS":
            matched = any(
                g_label == label and _address_match(text, g_text)
                for g_text, g_label in gold_set
            )
        else:
            matched = (text, label) in gold_set
        if not matched:
            stats[label]["fp_candidate"] = stats[label].get("fp_candidate", 0) + 1

    report = {}
    total_tp = total_fn = 0
    for label, s in sorted(stats.items()):
        tp, fn = s["tp"], s["fn"]
        total_tp += tp
        total_fn += fn
        recall = tp / (tp + fn) if (tp + fn) else None
        report[label] = {
            "TP": tp, "FN": fn,
            "recall": recall,
            "fp_candidates_for_manual_review": s.get("fp_candidate", 0),
        }

    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else None
    report["__OVERALL__"] = {"TP": total_tp, "FN": total_fn, "recall": overall_recall}
    return report


def fmt(v):
    return "N/A" if v is None else f"{v*100:.1f}%"


if __name__ == "__main__":
    report = evaluate("eval/ground_truth.json", "output/replacement_log.json")
    print(f"{'TYPE':<15}{'TP':<6}{'FN':<6}{'Recall':<10}{'FP candidates (review)':<25}")
    for label, s in report.items():
        if label == "__OVERALL__":
            continue
        print(f"{label:<15}{s['TP']:<6}{s['FN']:<6}{fmt(s['recall']):<10}"
              f"{s['fp_candidates_for_manual_review']:<25}")
    s = report["__OVERALL__"]
    print("-" * 60)
    print(f"{'OVERALL':<15}{s['TP']:<6}{s['FN']:<6}{fmt(s['recall']):<10}")

    Path("output/evaluation_report.json").write_text(json.dumps(report, indent=2))
    print("\nSaved: output/evaluation_report.json")