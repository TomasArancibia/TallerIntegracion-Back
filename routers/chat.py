import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from openai import OpenAI
from sqlalchemy.orm import Session
from typing import Optional
import os
import time

from db.session import SessionLocal
from models.models import PortalChatMessage


router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    id_cama: Optional[int] = None
    qr_code: Optional[str] = Field(default=None, max_length=64)
    portal_session_id: Optional[str] = Field(default=None, max_length=64)


def _persist_chat_message(
    db: Session,
    *,
    role: str,
    message: str,
    body: ChatRequest,
    thread_id: Optional[str] = None,
    run_id: Optional[str] = None,
):
    if not db:
        return
    try:
        event = PortalChatMessage(
            portal_session_id=body.portal_session_id,
            id_cama=body.id_cama,
            qr_code=body.qr_code,
            role=role,
            message=message,
            thread_id=thread_id,
            run_id=run_id,
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()


FALLBACK_REPLY = "Lo siento, el asistente virtual no está disponible en este momento."


@router.post("/chat")
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    if not api_key or not assistant_id:
        _persist_chat_message(db, role="user", message=body.message, body=body)
        _persist_chat_message(db, role="assistant", message=FALLBACK_REPLY, body=body)
        return {"reply": FALLBACK_REPLY}

    user_logged = False
    try:
        client = OpenAI(api_key=api_key)
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=body.message)
        _persist_chat_message(db, role="user", message=body.message, body=body, thread_id=thread.id)
        user_logged = True
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

        started = time.time()
        status = run
        while status.status not in ("completed", "failed", "cancelled") and (time.time() - started) < 60:
            time.sleep(0.8)
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if status.status != "completed":
            raise HTTPException(status_code=500, detail=f"Run no completado: {status.status}")

        msgs = client.beta.threads.messages.list(thread_id=thread.id, order="desc")
        reply = ""
        for m in msgs.data:
            if getattr(m, "role", None) == "assistant":
                parts = []
                for c in getattr(m, "content", []):
                    if getattr(c, "type", None) == "text" and getattr(c, "text", None):
                        parts.append(c.text.value)
                reply = "\n".join(parts).strip()
                break

        reply_payload = reply or "(Sin respuesta del asistente)"
        _persist_chat_message(
            db,
            role="assistant",
            message=reply_payload,
            body=body,
            thread_id=thread.id,
            run_id=run.id,
        )
        return {"reply": reply_payload}
    except Exception as exc:
        logger.exception("Fallo al contactar el asistente virtual: %s", exc)
        # Si la inserción anterior falló (por ejemplo, error antes de crear thread), la registramos ahora
        if not user_logged:
            _persist_chat_message(db, role="user", message=body.message, body=body)
        _persist_chat_message(db, role="assistant", message=FALLBACK_REPLY, body=body)
        return {"reply": FALLBACK_REPLY}


class ChatCompletionsRequest(BaseModel):
    message: str


@router.post("/chat-completions")
async def chat_completions(body: ChatCompletionsRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise HTTPException(status_code=500, detail="Falta OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente útil para un hospital."},
                {"role": "user", "content": body.message},
            ],
            temperature=0.2,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OpenAI: {e}")

    text = completion.choices[0].message.content if completion and completion.choices else ""
    return {"reply": (text or "").strip() or "(Sin respuesta del modelo)"}
