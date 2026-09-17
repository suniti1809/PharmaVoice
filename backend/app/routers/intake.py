"""AI intake endpoints - the entry points the AI Complaint Intake Assistant calls."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.agents import graph as agent_graph
from app.agents import llm, prompts
from app.config import settings
from app.database import get_db
from app.models import IntakeRun
from app.schemas import ChatRequest, ChatResponse, IntakeRequest, IntakeResponse
from app.services.documents import UnsupportedDocument, extract_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intake", tags=["intake"])


def _record_run(db: Session, *, kind: str, filename: str | None, text: str, result: IntakeResponse) -> None:
    db.add(
        IntakeRun(
            input_kind=kind,
            filename=filename,
            char_count=len(text),
            model_used=result.model_used,
            latency_ms=result.latency_ms,
            result=result.model_dump(mode="json"),
        )
    )
    db.commit()


@router.post("/text", response_model=IntakeResponse)
def intake_text(payload: IntakeRequest, db: Session = Depends(get_db)) -> IntakeResponse:
    """Run the LangGraph intake agent on pasted complaint text / email body."""
    result = agent_graph.run_intake(payload.text, db=db)
    _record_run(db, kind="text", filename=None, text=payload.text, result=result)
    return result


@router.post("/file", response_model=IntakeResponse)
async def intake_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> IntakeResponse:
    """Extract text from an uploaded complaint document, then run the same agent."""
    data = await file.read()
    limit = settings.max_upload_mb * 1024 * 1024
    if len(data) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_mb} MB limit.",
        )
    try:
        text = extract_text(file.filename or "upload", data)
    except UnsupportedDocument as exc:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(exc)) from exc
    except Exception as exc:  # corrupt file, encrypted PDF, ...
        logger.exception("document parsing failed")
        raise HTTPException(status_code=422, detail=f"Could not read the document: {exc}") from exc

    result = agent_graph.run_intake(text, db=db, filename=file.filename)
    _record_run(db, kind="file", filename=file.filename, text=text, result=result)
    return result


@router.post("/chat", response_model=ChatResponse)
def intake_chat(payload: ChatRequest) -> ChatResponse:
    """'Ask me anything about this complaint' box in the copilot panel."""
    try:
        result = llm.complete(
            prompts.CHAT_SYSTEM,
            prompts.chat_user(payload.question, payload.context_text, payload.form_state),
            chain=settings.extraction_chain,
        )
        return ChatResponse(answer=result.text, model_used=result.model)
    except llm.LLMUnavailable as exc:
        return ChatResponse(
            answer=(
                "The AI assistant is offline because no Groq API key is configured, so I can only "
                f"work from the form data on screen. ({exc})"
            ),
            model_used="unavailable",
        )
