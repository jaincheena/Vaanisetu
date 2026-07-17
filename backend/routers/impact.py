"""
VaaniSetu — Impact Router
GET /api/impact | POST /api/impact/config | GET /api/impact/export/pdf
"""

import os
import tempfile
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from backend.services.impact_ledger import get_impact_summary, update_impact_config, get_impact_config
from backend.services.export import export_impact_pdf
from backend.models.schemas import ImpactConfigUpdate
from backend.services.auth_service import require_admin

router = APIRouter(prefix="/api/impact", tags=["impact"])


@router.get("")
async def impact_summary(current_admin=Depends(require_admin)):
    return get_impact_summary()


@router.get("/config")
async def impact_config(current_admin=Depends(require_admin)):
    return get_impact_config()


@router.post("/config")
async def update_config(body: ImpactConfigUpdate, current_admin=Depends(require_admin)):
    update_impact_config(body.language, body.farmers_per_hour, body.translation_rate_per_min)
    return {"success": True}


@router.get("/export/pdf")
async def export_pdf(current_admin=Depends(require_admin)):
    summary = get_impact_summary()
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    export_impact_pdf(summary, tmp.name)
    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="vaanisetu_impact_report.pdf",
    )
