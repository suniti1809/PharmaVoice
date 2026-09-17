"""Lightweight document text extraction.

The assignment explicitly does not require production-grade OCR, so this module
covers the formats the UI advertises (PDF, DOCX, TXT, EML) with small, readable
parsers and a clear error when a format is unsupported.
"""

from __future__ import annotations

import io
import re
from email import message_from_bytes
from email.policy import default as default_policy

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".eml", ".md"}


class UnsupportedDocument(ValueError):
    pass


def _from_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _from_docx(data: bytes) -> str:
    import docx

    document = docx.Document(io.BytesIO(data))
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:  # complaint forms are often tabular
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(parts)


def _from_eml(data: bytes) -> str:
    message = message_from_bytes(data, policy=default_policy)
    header = "\n".join(
        f"{key}: {message[key]}" for key in ("From", "To", "Subject", "Date") if message[key]
    )
    body = message.get_body(preferencelist=("plain", "html"))
    text = body.get_content() if body else ""
    if body is not None and body.get_content_type() == "text/html":
        text = re.sub(r"<[^>]+>", " ", text)
    return f"{header}\n\n{text}"


def extract_text(filename: str, data: bytes) -> str:
    """Dispatch on file extension and normalise whitespace."""
    lowered = filename.lower()
    suffix = lowered[lowered.rfind(".") :] if "." in lowered else ""
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocument(
            f"Unsupported file type '{suffix or filename}'. Supported: PDF, DOCX, TXT, EML."
        )

    if suffix == ".pdf":
        text = _from_pdf(data)
    elif suffix == ".docx":
        text = _from_docx(data)
    elif suffix == ".eml":
        text = _from_eml(data)
    else:
        text = data.decode("utf-8", errors="replace")

    text = text.replace("\r\n", "\n").replace("\xa0", " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise UnsupportedDocument(
            "No text layer found in the document. Scanned images need OCR, which is out of scope."
        )
    return text
