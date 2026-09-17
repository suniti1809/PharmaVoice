"""Complaint register CRUD - what the Save Complaint button talks to."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Complaint
from app.schemas import ComplaintCreate, ComplaintOut, StatusUpdate

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _next_complaint_number(db: Session) -> str:
    """Human-readable QMS identifier: CC-<year>-<sequence>."""
    year = datetime.now(UTC).year
    prefix = f"CC-{year}-"
    count = db.scalar(select(func.count(Complaint.id)).where(Complaint.complaint_number.like(f"{prefix}%"))) or 0
    return f"{prefix}{count + 1:04d}"


@router.post("", response_model=ComplaintOut, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)) -> Complaint:
    if not payload.description:
        raise HTTPException(status_code=422, detail="A complaint description is required to open a record.")

    complaint = Complaint(**payload.model_dump(), complaint_number=_next_complaint_number(db))
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[ComplaintOut])
def list_complaints(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Match customer, product, batch or complaint number"),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, le=200),
) -> list[Complaint]:
    stmt = select(Complaint).order_by(Complaint.id.desc()).limit(limit)
    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Complaint.customer_name.ilike(like),
                Complaint.product_name.ilike(like),
                Complaint.batch_number.ilike(like),
                Complaint.complaint_number.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_status(complaint_id: int, payload: StatusUpdate, db: Session = Depends(get_db)) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint
