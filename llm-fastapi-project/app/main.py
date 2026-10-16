import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.llm_service import generate_response

app = FastAPI(
    title="Qwen Fine-Tuned Model API",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    max_new_tokens: int = Field(default=128, ge=1, le=256)


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def home():
    return {"message": "Qwen FastAPI server is running"}


@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = generate_response(
            request.message.strip(),
            request.max_new_tokens,
        )
        return ChatResponse(reply=reply)

    except Exception:
        logging.exception("Model generation failed")
        raise HTTPException(
            status_code=500,
            detail="Model generation failed. Check terminal logs.",
        )




import time
import logging

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.llm_service import generate_response

logger = logging.getLogger(__name__)


class PredictRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class PredictResponse(BaseModel):
    question: str
    answer: str
    model: str


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    start = time.perf_counter()

    try:
        answer = generate_response(
            question,
            max_new_tokens=180,
        )

        elapsed = time.perf_counter() - start
        logger.info("Prediction completed in %.2f seconds", elapsed)

        return PredictResponse(
            question=question,
            answer=answer,
            model="Qwen2.5-1.5B-Instruct + LoRA",
        )

    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check server logs.",
        )
