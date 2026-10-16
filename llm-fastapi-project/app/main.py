import logging
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.llm_service import MODEL_LABEL, generate_response

# INFO level is required for the per-request response-time logs below to appear.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Qwen2.5-1.5B + LoRA Technical Support Assistant API",
    description=(
        "Inference API for a LoRA fine-tuned Qwen2.5-1.5B-Instruct model "
        "that answers technical support questions."
    ),
    version="1.0.0",
)


class PredictRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class PredictResponse(BaseModel):
    question: str
    answer: str
    model: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    max_new_tokens: int = Field(default=128, ge=1, le=256)


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def home():
    return {"message": "Qwen2.5-1.5B + LoRA FastAPI server is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    question = request.question.strip()

    # min_length=1 lets whitespace-only strings through, so reject them here.
    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    start = time.perf_counter()

    try:
        answer = generate_response(question, max_new_tokens=180)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check server logs.",
        )

    elapsed = time.perf_counter() - start
    logger.info("Prediction completed in %.2f seconds", elapsed)

    return PredictResponse(
        question=question,
        answer=answer,
        model=MODEL_LABEL,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    start = time.perf_counter()

    try:
        reply = generate_response(message, request.max_new_tokens)
    except Exception:
        logger.exception("Model generation failed")
        raise HTTPException(
            status_code=500,
            detail="Model generation failed. Check terminal logs.",
        )

    elapsed = time.perf_counter() - start
    logger.info("Chat completed in %.2f seconds", elapsed)

    return ChatResponse(reply=reply)
