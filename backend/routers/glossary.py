"""
VaaniSetu — Glossary Router
GET /api/glossary | GET /api/glossary/export/docx
"""

import tempfile
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import FileResponse

from backend.database import get_db, rows_to_list
from backend.services.translation_memory import store_approved, get_glossary
from backend.services.auth_service import get_current_user, require_admin
from backend.services.export import export_glossary_docx

router = APIRouter(prefix="/api/glossary", tags=["glossary"])


@router.get("")
async def fetch_glossary(search: str = "", current_user: dict = Depends(get_current_user)):
    """Fetch Translation Memory entries (Glossary)."""
    terms = get_glossary()
    if search:
        q = search.lower()
        terms = [t for t in terms if q in t["source_text"].lower()]
    return terms


@router.get("/export/docx")
async def export_docx(current_admin: dict = Depends(require_admin)):
    terms = get_glossary()
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp.close()
    export_glossary_docx(terms, tmp.name)
    return FileResponse(
        tmp.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="vaanisetu_glossary.docx",
    )
