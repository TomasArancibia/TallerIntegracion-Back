from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import time


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(body: ChatRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    if not api_key or not assistant_id:
        raise HTTPException(status_code=500, detail="Faltan OPENAI_API_KEY u OPENAI_ASSISTANT_ID")

    client = OpenAI(api_key=api_key)
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=body.message)
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

    return {"reply": reply or "(Sin respuesta del asistente)"}


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


