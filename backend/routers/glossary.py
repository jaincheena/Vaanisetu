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

@router.delete("/{term_id}")
async def delete_glossary_term(term_id: int, current_user: dict = Depends(require_admin)):
    """
    Delete a glossary term by ID.
    Only admins can delete terms.
    """
    with get_db() as conn:
      cursor = conn.cursor()
      cursor.execute("DELETE FROM translation_memory WHERE id=?", (term_id,))
      conn.commit()
      if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Term not found")
      return {"success": True, "deleted_id": term_id}

class GlossaryTermCreate(BaseModel):
    source_text: str
    source_lang: str = "English"
    target_lang: str
    translated_text: str
    domain: str = "agriculture"


@router.post("")
async def add_glossary_term(body: GlossaryTermCreate, current_user: dict = Depends(get_current_user)):
    """Add a new verified agricultural term to Translation Memory."""
    store_approved(
        src_lang=body.source_lang,
        tgt_lang=body.target_lang,
        source_text=body.source_text,
        translated_text=body.translated_text,
    )
    return {"success": True, "message": f"Term '{body.source_text}' stored in glossary"}


@router.get("/export/docx")
async def export_docx(current_user: dict = Depends(get_current_user)):
    terms = get_glossary()
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp.close()
    export_glossary_docx(terms, tmp.name)
    return FileResponse(
        tmp.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="vaanisetu_glossary.docx",
    )
