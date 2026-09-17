"""Database models for the Customer Complaint module of a pharma QMS.

Field naming follows the vocabulary used on the Log Customer Complaint form so
the mapping between UI, API and DB stays obvious.
"""

from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    complaint_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    # 1. Origin & customer details
    complaint_source: Mapped[str | None] = mapped_column(String(64))
    customer_name: Mapped[str | None] = mapped_column(String(255), index=True)

    # 2. Product & batch identification
    product_name: Mapped[str | None] = mapped_column(String(255), index=True)
    product_strength: Mapped[str | None] = mapped_column(String(64))
    batch_number: Mapped[str | None] = mapped_column(String(64), index=True)
    manufacturing_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    quantity_affected: Mapped[float | None] = mapped_column(Numeric(12, 3))
    quantity_uom: Mapped[str | None] = mapped_column(String(16), default="kg")

    # 3. Complaint details
    complaint_type: Mapped[str | None] = mapped_column(String(64))
    complaint_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)

    # 4. Initial assessment & priority
    initial_severity: Mapped[str | None] = mapped_column(String(32))
    priority: Mapped[str | None] = mapped_column(String(32))

    # Workflow + AI assessment payload
    status: Mapped[str] = mapped_column(String(32), default="Pending Triage")
    ai_assessment: Mapped[dict | None] = mapped_column(JSON)
    source_document: Mapped[str | None] = mapped_column(String(255))
    raw_text: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class IntakeRun(Base):
    """Audit trail of every AI intake execution (QMS reviewers like traceability)."""

    __tablename__ = "intake_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    input_kind: Mapped[str] = mapped_column(String(16))  # text | file
    filename: Mapped[str | None] = mapped_column(String(255))
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    model_used: Mapped[str | None] = mapped_column(String(64))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
