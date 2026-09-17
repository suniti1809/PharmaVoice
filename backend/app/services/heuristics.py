"""Deterministic fallbacks used when the LLM is unavailable.

These are intentionally simple regex/keyword rules. Their job is to keep the
demo alive (and to give the graph a non-crashing degraded mode), not to compete
with the model. Every value they produce is marked low-confidence in the UI.
"""

from __future__ import annotations

import re
from datetime import datetime

from app.schemas import ExtractedComplaint

_DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "%Y-%m-%d"),
    (re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b"), "%d/%m/%Y"),
    (re.compile(r"\b(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b"), "%d %B %Y"),
]

_CRITICAL_TERMS = [
    "adverse event", "hospital", "patient harm", "sterility", "contamination",
    "wrong product", "wrong strength", "particulate", "injectable", "out of specification",
    "recall", "black particle",
]
_MAJOR_TERMS = ["discolor", "discolour", "label", "packaging", "dissolution", "assay", "odour", "odor", "coa", "impurity"]


def _search(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.I)
    return match.group(1).strip() if match else None


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    for pattern, fmt in _DATE_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        raw = match.group(0)
        for candidate_fmt in (fmt, "%d %b %Y"):
            try:
                return datetime.strptime(raw, candidate_fmt).date().isoformat()
            except ValueError:
                continue
    return None


def rule_based_extraction(text: str) -> ExtractedComplaint:
    quantity = _search(r"quantity(?:\s+affected)?\s*[:\-]?\s*([\d.,]+)", text)
    return ExtractedComplaint(
        complaint_source="Email" if re.search(r"^(from|subject)\s*:", text, re.I | re.M) else None,
        customer_name=_search(r"(?:customer|complainant|company)\s*(?:name)?\s*[:\-]\s*(.+)", text),
        product_name=_search(r"product\s*(?:name)?\s*[:\-]\s*(.+)", text),
        product_strength=_search(r"(?:strength|grade)\s*[:\-]\s*(.+)", text),
        batch_number=_search(r"(?:batch|lot)\s*(?:no\.?|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]{4,})", text),
        manufacturing_date=_parse_date(_search(r"(?:mfg|manufactur\w*)\s*date\s*[:\-]?\s*(.+)", text)),
        expiry_date=_parse_date(_search(r"(?:exp|expiry|expiration)\s*date\s*[:\-]?\s*(.+)", text)),
        quantity_affected=float(quantity.replace(",", "")) if quantity else None,
        complaint_type=None,
        complaint_date=_parse_date(_search(r"date\s*[:\-]?\s*(.+)", text)),
        description=" ".join(text.split())[:400],
        initial_severity=rule_based_severity(text),
    )


def rule_based_severity(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in _CRITICAL_TERMS):
        return "Critical"
    if any(term in lowered for term in _MAJOR_TERMS):
        return "Major"
    return "Minor"


def severity_to_priority(severity: str | None) -> str:
    return {
        "Critical": "P1 - Urgent",
        "Major": "P2 - High",
        "Minor": "P4 - Low",
    }.get(severity or "", "P3 - Medium")


def severity_to_risk(severity: str | None) -> tuple[int, str]:
    return {
        "Critical": (88, "Critical"),
        "Major": (60, "Medium"),
        "Minor": (25, "Low"),
    }.get(severity or "", (40, "Medium"))
