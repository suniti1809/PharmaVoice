"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import complaints, intake
from app.schemas import COMPLAINT_SOURCES, COMPLAINT_TYPES, PRIORITIES, SEVERITIES
from app.seed import seed_if_empty

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.auto_seed:
        seed_if_empty()
    logging.getLogger(__name__).info(
        "startup: db=%s llm=%s", settings.database_url.split("@")[-1], settings.llm_enabled
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered Customer Complaint intake for an API / FDF pharmaceutical QMS.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials="*" not in settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intake.router)
app.include_router(complaints.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    # Serverless containers are recycled, so make sure the schema/seed exist for
    # cold starts that skip the lifespan hook.
    init_db()
    if settings.auto_seed:
        seed_if_empty()
    return {
        "status": "ok",
        "llm_enabled": settings.llm_enabled,
        "extraction_models": settings.extraction_chain,
        "reasoning_models": settings.reasoning_chain,
    }


@app.get("/api/metadata", tags=["meta"])
def metadata() -> dict:
    """Dropdown options for the Log Customer Complaint form (single source of truth)."""
    return {
        "complaint_sources": COMPLAINT_SOURCES,
        "complaint_types": COMPLAINT_TYPES,
        "severities": SEVERITIES,
        "priorities": PRIORITIES,
        "uoms": ["kg", "g", "L", "mL", "vials", "bottles", "tablets", "packs"],
    }
