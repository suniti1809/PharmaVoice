"""Seed the complaint register with two closed records.

Having history in the DB is what makes Duplicate Complaint Detection visible in
the demo: uploading complaint_04 then matches the seeded particulate complaint.

Run:  python scripts/seed_database.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db  # noqa: E402
from app.models import Complaint  # noqa: E402

SEED = [
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


def main() -> None:
    init_db()
    with SessionLocal() as db:
        existing = {c.complaint_number for c in db.query(Complaint).all()}
        added = 0
        for complaint in SEED:
            if complaint.complaint_number in existing:
                continue
            db.add(complaint)
            added += 1
        db.commit()
    print(f"seeded {added} complaint(s)")


if __name__ == "__main__":
    main()
