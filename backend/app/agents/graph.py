"""LangGraph intake agent.

Graph shape (linear with one conditional guard):

    normalise_input
          |
      extract_fields ------(no usable text)------> finalise
          |
      validate_fields          (enum + date coercion, no LLM)
          |
      check_completeness       gemma2-9b-it   -> Completeness Checker
          |
      detect_duplicates        SQL + scoring  -> Duplicate Detection
          |
      assess_risk              llama-3.3-70b  -> Risk / RCA / CAPA / Summary
          |
        finalise               assembles IntakeResponse

Each node is a pure function of the state dict, which makes the workflow easy to
unit-test and easy to explain in the demo video: state goes in, an enriched copy
of the state comes out, and `trace` records what happened.
"""

from __future__ import annotations

import logging
import time
from datetime import date, datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents import llm, prompts
from app.config import settings
from app.schemas import (
    COMPLAINT_SOURCES,
    COMPLAINT_TYPES,
    PRIORITIES,
    SEVERITIES,
    CompletenessReport,
    DuplicateMatch,
    ExtractedComplaint,
    FieldConfidence,
    IntakeResponse,
    RiskAssessment,
)
from app.services import duplicates as dup_service
from app.services import heuristics


def _short_summary(text: str, limit: int = 260) -> str:
    """Trim a fallback summary to whole sentences so the UI never shows a word
    cut in half (the rule-based path echoes the source text)."""
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    cut = clean[:limit]
    for sep in (". ", "! ", "? "):
        idx = cut.rfind(sep)
        if idx > 80:
            return cut[: idx + 1]
    return cut.rsplit(" ", 1)[0] + "\u2026"


logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "customer_name",
    "product_name",
    "batch_number",
    "complaint_type",
    "complaint_date",
    "description",
    "quantity_affected",
]


class IntakeState(TypedDict, total=False):
    raw_text: str
    filename: str | None
    db: Any  # SQLAlchemy Session - carried in state so nodes stay dependency-free
    extracted: dict
    confidence: list[dict]
    completeness: dict
    duplicates: list[dict]
    risk: dict
    trace: list[str]
    model_used: str
    degraded: bool


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _log(state: IntakeState, message: str) -> list[str]:
    trace = list(state.get("trace", []))
    trace.append(message)
    logger.info("[intake] %s", message)
    return trace


def _closest_enum(value: str | None, allowed: list[str]) -> str | None:
    """Snap a model answer onto an allowed enum value (case/substring tolerant)."""
    if not value:
        return None
    cleaned = value.strip()
    for option in allowed:
        if cleaned.lower() == option.lower():
            return option
    for option in allowed:
        if cleaned.lower() in option.lower() or option.lower() in cleaned.lower():
            return option
    return None


def _coerce_date(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%d %b %Y", "%d %B %Y", "%b %Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _coerce_number(value: Any) -> float | None:
    if value in (None, "", "null"):
        return None
    try:
        return float(str(value).replace(",", "").split()[0])
    except (ValueError, IndexError):
        return None


# --------------------------------------------------------------------------- #
# nodes
# --------------------------------------------------------------------------- #
def normalise_input(state: IntakeState) -> IntakeState:
    text = (state.get("raw_text") or "").strip()
    return {
        "raw_text": text,
        "trace": _log(state, f"normalise_input: {len(text)} characters received"),
        "degraded": False,
    }


def extract_fields(state: IntakeState) -> IntakeState:
    """Pull form fields out of the document with the small extraction model."""
    text = state["raw_text"]
    try:
        payload, model = llm.complete_json(
            prompts.EXTRACTION_SYSTEM,
            prompts.extraction_user(text),
            chain=settings.extraction_chain,
        )
        confidence = payload.pop("confidence", []) or []
        extracted = ExtractedComplaint(
            **{k: v for k, v in payload.items() if k in ExtractedComplaint.model_fields}
        )
        return {
            "extracted": extracted.model_dump(),
            "confidence": confidence,
            "model_used": model,
            "trace": _log(state, f"extract_fields: extraction model populated {sum(1 for v in extracted.model_dump().values() if v not in (None, ''))} fields"),
        }
    except llm.LLMUnavailable as exc:
        extracted = heuristics.rule_based_extraction(text)
        return {
            "extracted": extracted.model_dump(),
            "confidence": [
                {"field": k, "confidence": 0.35, "evidence": "regex fallback"}
                for k, v in extracted.model_dump().items()
                if v not in (None, "")
            ],
            "model_used": "rule-based-fallback",
            "degraded": True,
            "trace": _log(state, f"extract_fields: LLM unavailable ({exc}); used regex fallback"),
        }


def validate_fields(state: IntakeState) -> IntakeState:
    """Deterministic clean-up so the frontend never receives an invalid enum/date."""
    data = dict(state["extracted"])

    data["complaint_source"] = _closest_enum(data.get("complaint_source"), COMPLAINT_SOURCES)
    data["complaint_type"] = _closest_enum(data.get("complaint_type"), COMPLAINT_TYPES)
    data["initial_severity"] = _closest_enum(data.get("initial_severity"), SEVERITIES)
    data["priority"] = _closest_enum(data.get("priority"), PRIORITIES)

    for field in ("manufacturing_date", "expiry_date", "complaint_date"):
        data[field] = _coerce_date(data.get(field))
    data["quantity_affected"] = _coerce_number(data.get("quantity_affected"))
    data["quantity_uom"] = (data.get("quantity_uom") or "kg")[:16]

    # Sanity rule from GMP practice: expiry must be after manufacturing date.
    notes = []
    if data["manufacturing_date"] and data["expiry_date"] and data["expiry_date"] < data["manufacturing_date"]:
        data["manufacturing_date"], data["expiry_date"] = data["expiry_date"], data["manufacturing_date"]
        notes.append("swapped mfg/expiry dates (expiry preceded manufacturing)")

    filled = sum(1 for v in data.values() if v not in (None, "", []))
    return {
        "extracted": data,
        "trace": _log(state, f"validate_fields: {filled} fields populated" + (f"; {'; '.join(notes)}" if notes else "")),
    }


def check_completeness(state: IntakeState) -> IntakeState:
    """Bonus feature: Complaint Completeness Checker."""
    data = state["extracted"]
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    deterministic_score = round(100 * (len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS))

    try:
        payload, source = llm.complete_json(
            prompts.COMPLETENESS_SYSTEM,
            prompts.completeness_user(data),
            chain=settings.extraction_chain,
        )
        # The model is good at writing follow-up questions but is inconsistent
        # about arithmetic (it will happily return 100 while listing gaps), so the
        # deterministic count is treated as the ceiling and the model's extra
        # observations are merged in - but only for fields that really are empty.
        # Only required fields drive the score and the "missing" list, so the two
        # can never disagree on screen. Extra observations from the model become
        # follow-up questions instead.
        model_missing = [
            f for f in (payload.get("missing_fields") or [])
            if isinstance(f, str) and f in REQUIRED_FIELDS and not data.get(f)
        ]
        merged_missing = list(dict.fromkeys(missing + model_missing))
        model_score = _coerce_number(payload.get("score"))
        report = CompletenessReport(
            score=min(deterministic_score, int(model_score)) if model_score is not None else deterministic_score,
            missing_fields=merged_missing,
            follow_up_questions=(payload.get("follow_up_questions") or [])[:4],
        )
    except llm.LLMUnavailable:
        report = CompletenessReport(
            score=deterministic_score,
            missing_fields=missing,
            follow_up_questions=[
                f"Please provide the {f.replace('_', ' ')} for this complaint." for f in missing[:4]
            ],
        )
        source = "rule-based"

    return {
        "completeness": report.model_dump(),
        "trace": _log(state, f"check_completeness: score {report.score}/100 via {source}"),
    }


def detect_duplicates(state: IntakeState) -> IntakeState:
    """Bonus feature: Duplicate Complaint Detection."""
    db: Session | None = state.get("db")
    if db is None:
        return {"duplicates": [], "trace": _log(state, "detect_duplicates: skipped (no db session)")}

    matches = dup_service.find_duplicates(db, ExtractedComplaint(**state["extracted"]))
    return {
        "duplicates": [m.model_dump() for m in matches],
        "trace": _log(state, f"detect_duplicates: {len(matches)} possible duplicate(s)"),
    }


def assess_risk(state: IntakeState) -> IntakeState:
    """Bonus features: Risk Classification + Root Cause + CAPA + Summary.

    Uses the larger reasoning chain because this node reasons over the full
    document plus recurrence context, not just field spotting.
    """
    data = state["extracted"]
    try:
        payload, source = llm.complete_json(
            prompts.RISK_SYSTEM,
            prompts.risk_user(data, state["raw_text"], state.get("duplicates", [])),
            chain=settings.reasoning_chain,
        )
        risk = RiskAssessment(
            severity=_closest_enum(payload.get("severity"), SEVERITIES),
            priority=_closest_enum(payload.get("priority"), PRIORITIES),
            risk_score=max(0, min(100, int(_coerce_number(payload.get("risk_score")) or 0))),
            risk_band=payload.get("risk_band"),
            regulatory_reportable=bool(payload.get("regulatory_reportable")),
            rationale=payload.get("rationale"),
            recommended_actions=payload.get("recommended_actions") or [],
            probable_root_causes=payload.get("probable_root_causes") or [],
            capa_recommendations=payload.get("capa_recommendations") or [],
            summary=payload.get("summary"),
        )
    except llm.LLMUnavailable as exc:
        severity = data.get("initial_severity") or heuristics.rule_based_severity(state["raw_text"])
        score, band = heuristics.severity_to_risk(severity)
        risk = RiskAssessment(
            severity=severity,
            priority=heuristics.severity_to_priority(severity),
            risk_score=score,
            risk_band=band,
            regulatory_reportable=severity == "Critical",
            rationale=f"Keyword-based classification (LLM unavailable: {exc}).",
            recommended_actions=[
                "Acknowledge the complaint to the customer within 2 working days.",
                "Retrieve batch manufacturing and packaging records for review.",
                "Request the complaint sample and photographs from the customer.",
            ],
            summary=_short_summary(data.get("description") or state["raw_text"]),
        )
        source = "rule-based"

    # Escalation rule: a recurring defect on the same batch is never low risk.
    if state.get("duplicates") and risk.risk_score < 60:
        risk.risk_score = 60
        risk.risk_band = "High"
        risk.rationale = (risk.rationale or "") + " Escalated: similar complaint already exists (recurrence)."

    # Keep the form's severity/priority aligned with the copilot's assessment
    # when extraction left them blank - this is what the demo shows.
    extracted = dict(data)
    extracted["initial_severity"] = extracted.get("initial_severity") or risk.severity
    extracted["priority"] = extracted.get("priority") or risk.priority

    return {
        "risk": risk.model_dump(),
        "extracted": extracted,
        "trace": _log(state, f"assess_risk: {risk.severity} / score {risk.risk_score} via {source}"),
    }


def finalise(state: IntakeState) -> IntakeState:
    return {"trace": _log(state, "finalise: response assembled")}


def _has_text(state: IntakeState) -> str:
    return "extract" if len(state.get("raw_text", "")) >= 10 else "empty"


# --------------------------------------------------------------------------- #
# graph construction (compiled once at import time)
# --------------------------------------------------------------------------- #
def build_graph():
    builder = StateGraph(IntakeState)
    builder.add_node("normalise_input", normalise_input)
    builder.add_node("extract_fields", extract_fields)
    builder.add_node("validate_fields", validate_fields)
    builder.add_node("check_completeness", check_completeness)
    builder.add_node("detect_duplicates", detect_duplicates)
    builder.add_node("assess_risk", assess_risk)
    builder.add_node("finalise", finalise)

    builder.set_entry_point("normalise_input")
    builder.add_conditional_edges(
        "normalise_input",
        _has_text,
        {"extract": "extract_fields", "empty": "finalise"},
    )
    builder.add_edge("extract_fields", "validate_fields")
    builder.add_edge("validate_fields", "check_completeness")
    builder.add_edge("check_completeness", "detect_duplicates")
    builder.add_edge("detect_duplicates", "assess_risk")
    builder.add_edge("assess_risk", "finalise")
    builder.add_edge("finalise", END)
    return builder.compile()


INTAKE_GRAPH = build_graph()


def run_intake(raw_text: str, db: Session | None = None, filename: str | None = None) -> IntakeResponse:
    """Execute the graph and shape the result into the API response model."""
    started = time.perf_counter()
    final_state: IntakeState = INTAKE_GRAPH.invoke(
        {"raw_text": raw_text, "db": db, "filename": filename, "trace": []}
    )
    latency_ms = int((time.perf_counter() - started) * 1000)

    extracted = ExtractedComplaint(**(final_state.get("extracted") or {}))
    completeness = CompletenessReport(
        **(final_state.get("completeness") or {"score": 0, "missing_fields": REQUIRED_FIELDS})
    )
    risk = RiskAssessment(**(final_state.get("risk") or {}))

    confidence = [
        FieldConfidence(
            field=str(item.get("field", "")),
            confidence=max(0.0, min(1.0, float(item.get("confidence", 0) or 0))),
            evidence=(str(item.get("evidence")) if item.get("evidence") else None),
        )
        for item in (final_state.get("confidence") or [])
        if isinstance(item, dict) and item.get("field")
    ]

    return IntakeResponse(
        extracted=extracted,
        confidence=confidence,
        completeness=completeness,
        risk=risk,
        duplicates=[DuplicateMatch(**d) for d in final_state.get("duplicates", [])],
        trace=final_state.get("trace", []),
        model_used=final_state.get("model_used", "unknown"),
        latency_ms=latency_ms,
        raw_text_preview=raw_text[:1200],
    )
