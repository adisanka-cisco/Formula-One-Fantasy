import os
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Formula One Fantasy AI Assistant")


class AdviceRequest(BaseModel):
    race_id: int
    question: str
    current_prediction: Dict[str, Any] = {}


class AdviceResponse(BaseModel):
    advice: str
    model_enabled: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/advice", response_model=AdviceResponse)
def advice(payload: AdviceRequest):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return AdviceResponse(
            advice=(
                "AI model access is not configured yet. For now, compare driver form, qualifying position, "
                "team pace, pit crew consistency, and recent reliability before submitting the prediction."
            ),
            model_enabled=False,
        )

    return AdviceResponse(
        advice=(
            "OpenAI integration is ready to be added. This foundation service received your question and "
            "will call the model once the integration code is enabled."
        ),
        model_enabled=False,
    )

