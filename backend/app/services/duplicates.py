"""Duplicate / recurrence detection against complaints already in the database.

Approach: cheap deterministic scoring, no embeddings needed.
  batch number match ....... 0.55  (strongest signal in a QMS)
  customer match ........... 0.15
  product match ............ 0.15
  description similarity ... 0.15  (token Jaccard)
Anything at or above 0.45 is surfaced to the reviewer as a possible duplicate.
"""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Complaint
from app.schemas import DuplicateMatch, ExtractedComplaint

THRESHOLD = 0.45
_STOPWORDS = {
    "the", "and", "for", "with", "was", "were", "has", "have", "from", "that", "this",
    "our", "your", "batch", "product", "complaint", "received", "please", "been",
}


def _tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    words = re.findall(r"[a-z0-9]{3,}", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _norm(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def find_duplicates(db: Session, candidate: ExtractedComplaint, limit: int = 3) -> list[DuplicateMatch]:
    existing = db.scalars(select(Complaint).order_by(Complaint.id.desc()).limit(300)).all()
    candidate_tokens = _tokens(candidate.description)
    matches: list[DuplicateMatch] = []

    for row in existing:
        score = 0.0
        reasons: list[str] = []

        if candidate.batch_number and _norm(candidate.batch_number) == _norm(row.batch_number):
            score += 0.55
            reasons.append(f"same batch {row.batch_number}")
        if candidate.customer_name and _norm(candidate.customer_name) == _norm(row.customer_name):
            score += 0.15
            reasons.append("same customer")
        if candidate.product_name and _norm(candidate.product_name) == _norm(row.product_name):
            score += 0.15
            reasons.append("same product")

        text_similarity = _jaccard(candidate_tokens, _tokens(row.description))
        if text_similarity > 0.2:
            score += 0.15 * text_similarity / max(text_similarity, 1.0)
            score += min(text_similarity, 0.15)
            reasons.append(f"description overlap {text_similarity:.0%}")

        if score >= THRESHOLD:
            matches.append(
                DuplicateMatch(
                    complaint_number=row.complaint_number,
                    customer_name=row.customer_name,
                    batch_number=row.batch_number,
                    similarity=round(min(score, 1.0), 2),
                    reason=", ".join(reasons),
                )
            )

    matches.sort(key=lambda m: m.similarity, reverse=True)
    return matches[:limit]
