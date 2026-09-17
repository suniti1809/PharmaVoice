"""Demo history for the complaint register.

Two closed/under-investigation records are inserted on first boot. They give the
register something to show and, more importantly, give Duplicate Complaint
Detection a record to match against (sample_data/complaint_04 duplicates
CC-2026-0001).
"""

from __future__ import annotations

import logging
from datetime import date

from app.database import SessionLocal
from app.models import Complaint

logger = logging.getLogger(__name__)


def _records() -> list[Complaint]:
    return [
        Complaint(
            complaint_number="CC-2026-0001",
            complaint_source="Email",
            customer_name="Nordwell Formulations GmbH",
            product_name="Metformin Hydrochloride IP",
            product_strength="USP Grade, D90 45 um",
            batch_number="MTF-2509-118",
            manufacturing_date=date(2025, 11, 18),
            expiry_date=date(2027, 11, 17),
            quantity_affected=125,
            quantity_uom="kg",
            complaint_type="Foreign Particulate Matter",
            complaint_date=date(2026, 3, 4),
            description=(
                "Black fibrous particulate matter observed in two of five HDPE drums of "
                "Metformin Hydrochloride IP batch MTF-2509-118 during dispensing."
            ),
            initial_severity="Critical",
            priority="P1 - Urgent",
            status="Under Investigation",
        ),
        Complaint(
            complaint_number="CC-2026-0002",
            complaint_source="Customer Portal",
            customer_name="Halden Pharma Nordic AB",
            product_name="Ibuprofen Tablets",
            product_strength="400 mg",
            batch_number="IBU-2508-091",
            manufacturing_date=date(2025, 8, 22),
            expiry_date=date(2028, 8, 21),
            quantity_affected=60,
            quantity_uom="packs",
            complaint_type="Packaging Defect",
            complaint_date=date(2026, 1, 27),
            description="Blister pockets partially unsealed in 60 packs; no tablet damage reported.",
            initial_severity="Major",
            priority="P2 - High",
            status="Closed",
        ),
    ]


def seed_if_empty() -> int:
    """Insert the demo records when the register has no rows. Returns rows added."""
    try:
        with SessionLocal() as db:
            if db.query(Complaint).count():
                return 0
            records = _records()
            db.add_all(records)
            db.commit()
            logger.info("seeded %d demo complaint(s)", len(records))
            return len(records)
    except Exception as exc:  # never block startup on seeding
        logger.warning("seed skipped: %s", exc)
        return 0
