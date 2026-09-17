"""Pydantic contracts shared by the API and the LangGraph agent."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

COMPLAINT_SOURCES = ["Email", "Phone", "Customer Portal", "Distributor", "Regulatory Authority", "Field Alert"]
COMPLAINT_TYPES = [
    "Quality Defect",
    "Packaging Defect",
    "Labeling Error",
    "Documentation / CoA",
    "Foreign Particulate Matter",
    "Out of Specification",
    "Shipping / Logistics Damage",
    "Adverse Event",
    "Other",
]
SEVERITIES = ["Critical", "Major", "Minor"]
PRIORITIES = ["P1 - Urgent", "P2 - High", "P3 - Medium", "P4 - Low"]


# --------------------------------------------------------------------------- #
# Extraction (what the AI writes into the Log Customer Complaint form)
# --------------------------------------------------------------------------- #
class ExtractedComplaint(BaseModel):
    """Every field is optional: the agent must be allowed to say 'not stated'."""

    complaint_source: str | None = None
    customer_name: str | None = None
    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    quantity_affected: float | None = None
    quantity_uom: str | None = "kg"
    complaint_type: str | None = None
    complaint_date: str | None = None
    description: str | None = None
    initial_severity: str | None = None
    priority: str | None = None


class FieldConfidence(BaseModel):
    field: str
    confidence: float = Field(ge=0, le=1)
    evidence: str | None = None


class CompletenessReport(BaseModel):
    score: int = Field(ge=0, le=100)
    missing_fields: list[str] = []
    follow_up_questions: list[str] = []


class RiskAssessment(BaseModel):
    severity: str | None = None
    priority: str | None = None
    risk_score: int = Field(default=0, ge=0, le=100)
    risk_band: str | None = None
    regulatory_reportable: bool = False
    rationale: str | None = None
    recommended_actions: list[str] = []
    probable_root_causes: list[str] = []
    capa_recommendations: list[str] = []
    summary: str | None = None


class DuplicateMatch(BaseModel):
    complaint_number: str
    customer_name: str | None = None
    batch_number: str | None = None
    similarity: float
    reason: str


class IntakeRequest(BaseModel):
    text: str = Field(min_length=10, description="Pasted complaint email or free text")


class IntakeResponse(BaseModel):
    extracted: ExtractedComplaint
    confidence: list[FieldConfidence] = []
    completeness: CompletenessReport
    risk: RiskAssessment
    duplicates: list[DuplicateMatch] = []
    trace: list[str] = []
    model_used: str
    latency_ms: int
    raw_text_preview: str


# --------------------------------------------------------------------------- #
# Complaint CRUD
# --------------------------------------------------------------------------- #
class ComplaintCreate(BaseModel):
    complaint_source: str | None = None
    customer_name: str | None = None
    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    quantity_affected: float | None = None
    quantity_uom: str | None = "kg"
    complaint_type: str | None = None
    complaint_date: date | None = None
    description: str | None = None
    initial_severity: str | None = None
    priority: str | None = None
    ai_assessment: dict | None = None
    source_document: str | None = None
    raw_text: str | None = None


class ComplaintOut(ComplaintCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_number: str
    status: str
    created_at: datetime


class ChatRequest(BaseModel):
    question: str = Field(min_length=2)
    context_text: str | None = None
    form_state: dict | None = None


class ChatResponse(BaseModel):
    answer: str
    model_used: str


class StatusUpdate(BaseModel):
    status: Literal["Pending Triage", "Under Investigation", "CAPA Initiated", "Closed", "Rejected"]
