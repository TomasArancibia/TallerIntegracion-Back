from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.models import Cama, Habitacion, Piso, Edificio, Institucion
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import RedirectResponse, StreamingResponse
import os
import qrcode
import io
import zipfile
import time

router = APIRouter()

# ================ DB dependency ================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================ Schemas (salida limpia) ================
class QRContext(BaseModel):
    ok: bool
    code: str
    id_cama: Optional[int] = None
    id_habitacion: Optional[int] = None
    id_hospital: Optional[int] = None
    hospital: Optional[str] = None
    habitacion: Optional[str] = None
    reason: Optional[str] = None

class BatchReq(BaseModel):
    codes: List[str]

# ================ Utils ================
def _qr_png_bytes(payload: str) -> bytes:
    """
    Genera una imagen PNG (bytes) con el contenido 'payload'.
    """
    img = qrcode.make(payload)  # simple y robusto
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ================ Validate ================
@router.get("/qr/validate", response_model=QRContext, summary="Valida un QR y entrega contexto")
def validate_qr(code: str, db: Session = Depends(get_db)):
    cama = db.query(Cama).filter(Cama.identificador_qr == code).first()
    if not cama:
        return QRContext(ok=False, code=code, reason="not_found")
    if cama.activo is False:
        return QRContext(ok=False, code=code, reason="inactive")

    hab = db.query(Habitacion).filter(Habitacion.id_habitacion == cama.id_habitacion).first()

    inst = None
    if hab:
        piso = db.query(Piso).filter(Piso.id_piso == hab.id_piso).first()
        if piso:
            edificio = db.query(Edificio).filter(Edificio.id_edificio == piso.id_edificio).first()
            if edificio:
                inst = (
                    db.query(Institucion)
                    .filter(Institucion.id_institucion == edificio.id_institucion)
                    .first()
                )

    return QRContext(
        ok=True,
        code=code,
        id_cama=cama.id_cama,
        id_habitacion=hab.id_habitacion if hab else None,
        id_hospital=inst.id_institucion if inst else None,
        hospital=inst.nombre_institucion if inst else None,
        habitacion=hab.nombre_habitacion if hab else None,
    )

# ================ Redirect (opcional, práctico para imprimir) ================
@router.get("/qr/redirect/{code}", summary="Redirige al landing del frontend con el QR en querystring")
def redirect_qr(code: str):
    base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    url = f"{base}/landing?qr={code}"
    return RedirectResponse(url=url, status_code=302)

# ================ Generar QR (DEV ONLY) ================
@router.get("/qr/generate/{code}", summary="Genera PNG de un QR (uso dev)")
def generate_qr_png(code: str):
    base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    # Si prefieres que el QR apunte al backend: payload = f"http://127.0.0.1:8000/qr/redirect/{code}"
    payload = f"{base}/landing?qr={code}"
    png = _qr_png_bytes(payload)
    return StreamingResponse(io.BytesIO(png), media_type="image/png")

@router.post("/qr/generate/batch", summary="Genera varios QRs y devuelve un ZIP (uso dev)")
def generate_qr_batch(body: BatchReq = Body(...)):
    """
    Envía {"codes": ["H1-101-A", "H1-101-B", ...]} y descarga un .zip con PNGs.
    """
    base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    zip_buf = io.BytesIO()

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for code in body.codes:
            payload = f"{base}/landing?qr={code}"
            png = _qr_png_bytes(payload)
            zf.writestr(f"{code}.png", png)

    zip_buf.seek(0)
    filename = f"qr_labels_{int(time.time())}.zip"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(zip_buf, media_type="application/zip", headers=headers)
