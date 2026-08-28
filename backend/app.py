from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000").rstrip("/")
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "120"))
try:
    TEHRAN_TZ = ZoneInfo("Asia/Tehran")
except Exception:
    # Windows may not have the IANA timezone database installed yet.
    # tzdata is listed in requirements.txt; this keeps the app usable
    # until dependencies are reinstalled.
    TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30), name="Asia/Tehran")

app = FastAPI(title="Persian VQA Backend", version="1.0.0")


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    model: str | None = None


async def ask_ai(question: str, system: str | None = None) -> AnswerResponse:
    payload = {"question": question}
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{AI_SERVICE_URL}/v1/chat", json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"اتصال به سرویس هوش مصنوعی برقرار نشد: {exc}",
        ) from exc

    return AnswerResponse(
        question=question,
        answer=data["answer"],
        model=data.get("model"),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "ai_service_url": AI_SERVICE_URL}


@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest) -> AnswerResponse:
    return await ask_ai(request.question)


@app.get("/ask-fixed", response_model=AnswerResponse)
async def ask_fixed() -> AnswerResponse:
    question = "سلام امروز چه روزیه؟"
    now = datetime.now(TEHRAN_TZ)
    system = (
        "به فارسی پاسخ بده. تاریخ امروز بر اساس ساعت ایران "
        f"{now.strftime('%Y-%m-%d')} است. اگر درباره روز هفته پرسیده شد، "
        "همین تاریخ را مبنا قرار بده و پاسخ کوتاه و دقیق بده."
    )
    return await ask_ai(question, system)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
