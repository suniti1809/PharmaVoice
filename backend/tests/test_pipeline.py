"""Tests that run without a Groq key (the graph falls back to rules)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pharmavoice.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.agents.graph import _closest_enum, _coerce_date, run_intake  # noqa: E402
from app.database import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas import SEVERITIES  # noqa: E402
from app.services.documents import UnsupportedDocument, extract_text  # noqa: E402

SAMPLE = """Customer Name: Nordwell Formulations GmbH
Product Name: Metformin Hydrochloride IP
Batch Number: MTF-2509-118
Mfg Date: 2025-11-18
Expiry Date: 2027-11-17
Quantity Affected: 125 kg
Black fibrous particulate matter found in two drums during dispensing.
"""


@pytest.fixture(scope="module")
def client():
    init_db()
    return TestClient(app)


def test_date_coercion():
    assert _coerce_date("2026-03-04") == "2026-03-04"
    assert _coerce_date("04/03/2026") == "2026-03-04"
    assert _coerce_date("not a date") is None


def test_enum_snapping():
    assert _closest_enum("critical", SEVERITIES) == "Critical"
    assert _closest_enum("banana", SEVERITIES) is None


def test_text_extraction_rejects_unknown_format():
    with pytest.raises(UnsupportedDocument):
        extract_text("scan.tiff", b"data")


def test_graph_runs_and_flags_critical():
    result = run_intake(SAMPLE)
    assert result.extracted.batch_number == "MTF-2509-118"
    assert result.risk.severity == "Critical"  # particulate keyword rule
    assert result.completeness.score >= 0
    assert len(result.trace) >= 5


def test_intake_and_save_roundtrip(client):
    response = client.post("/api/intake/text", json={"text": SAMPLE})
    assert response.status_code == 200
    extracted = response.json()["extracted"]

    payload = {k: v for k, v in extracted.items() if v is not None}
    payload["description"] = payload.get("description") or "fallback description"
    created = client.post("/api/complaints", json=payload)
    assert created.status_code == 201
    assert created.json()["complaint_number"].startswith("CC-")

    listing = client.get("/api/complaints")
    assert listing.status_code == 200
    assert len(listing.json()) >= 1


def test_metadata_endpoint(client):
    body = client.get("/api/metadata").json()
    assert "Critical" in body["severities"]
