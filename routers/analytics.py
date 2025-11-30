from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.models import PortalButtonEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ButtonClickIn(BaseModel):
    button_code: str = Field(..., min_length=1, max_length=120)
    button_label: Optional[str] = Field(None, max_length=160)
    categoria: Optional[str] = Field(None, max_length=60)
    source_path: Optional[str] = Field(None, max_length=160)
    target_path: Optional[str] = Field(None, max_length=160)
    id_cama: Optional[int]
    qr_code: Optional[str] = Field(None, max_length=64)
    portal_session_id: Optional[str] = Field(None, max_length=64)
    payload: Optional[Dict[str, Any]] = None

    @validator("button_code")
    def _strip_code(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("button_code no puede estar vacío")
        return cleaned

    @validator(
        "button_label", "categoria", "source_path", "target_path", "qr_code", "portal_session_id", pre=True
    )
    def _strip_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


@router.post("/button-click", status_code=201, summary="Registra un click en el portal QR")
def register_button_click(
    payload: ButtonClickIn,
    db: Session = Depends(get_db),
):
    event = PortalButtonEvent(
        button_code=payload.button_code,
        button_label=payload.button_label,
        categoria=payload.categoria,
        source_path=payload.source_path,
        target_path=payload.target_path,
        id_cama=payload.id_cama,
        qr_code=payload.qr_code,
        portal_session_id=payload.portal_session_id,
        payload=payload.payload,
    )
    db.add(event)
    db.commit()
    return {"ok": True}
