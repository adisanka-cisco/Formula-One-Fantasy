from datetime import datetime
from typing import List

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, hash_password, verify_password
from .config import AI_ASSISTANT_URL
from .db import get_db
from .models import Driver, Prediction, PredictionItem, Race, RaceResult, Team, User
from .schemas import (
    AssistantRequest,
    AssistantResponse,
    DriverResponse,
    LeaderboardEntry,
    LoginRequest,
    PredictionCreate,
    PredictionResponse,
    RaceResponse,
    RaceResultsRequest,
    RegisterRequest,
    TeamResponse,
    TokenResponse,
    UserResponse,
)
from .scoring import PREDICTION_TYPES, score_race


app = FastAPI(title="Formula One Fantasy API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == payload.email) | (User.nickname == payload.nickname)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or nickname already exists")

    user = User(
        nickname=payload.nickname,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        subscription_tier=payload.subscription_tier,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user))


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user.last_activity_at = datetime.utcnow()
    db.commit()
    return TokenResponse(access_token=create_access_token(user))


@app.get("/api/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/races", response_model=List[RaceResponse])
def races(db: Session = Depends(get_db)):
    return db.query(Race).order_by(Race.season, Race.round).all()


@app.get("/api/races/{race_id}", response_model=RaceResponse)
def race_detail(race_id: int, db: Session = Depends(get_db)):
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@app.get("/api/drivers", response_model=List[DriverResponse])
def drivers(db: Session = Depends(get_db)):
    return db.query(Driver).filter(Driver.active.is_(True)).order_by(Driver.driver_code).all()


@app.get("/api/teams", response_model=List[TeamResponse])
def teams(db: Session = Depends(get_db)):
    return db.query(Team).filter(Team.active.is_(True)).order_by(Team.name).all()


@app.post("/api/predictions", response_model=PredictionResponse)
def create_prediction(
    payload: PredictionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    race = db.query(Race).filter(Race.id == payload.race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    if race.status != "open_for_predictions":
        raise HTTPException(status_code=400, detail="Predictions are not open for this race")

    for item in payload.items:
        if item.prediction_type not in PREDICTION_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported prediction type: {item.prediction_type}")

    existing = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.race_id == payload.race_id,
    ).first()
    if existing:
        db.delete(existing)
        db.flush()

    prediction = Prediction(
        user_id=current_user.id,
        race_id=payload.race_id,
        stake_amount=payload.stake_amount,
        status="submitted",
    )
    prediction.items = [
        PredictionItem(
            prediction_type=item.prediction_type,
            position=item.position,
            driver_id=item.driver_id,
            team_id=item.team_id,
        )
        for item in payload.items
    ]
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@app.get("/api/predictions/me", response_model=List[PredictionResponse])
def my_predictions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).all()


@app.get("/api/predictions/me/{race_id}", response_model=PredictionResponse)
def my_prediction_for_race(race_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    prediction = db.query(Prediction).filter(Prediction.user_id == current_user.id, Prediction.race_id == race_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.status == "active").order_by(User.fantasy_score.desc(), User.nickname).limit(50).all()
    return [LeaderboardEntry(user_id=user.id, nickname=user.nickname, fantasy_score=user.fantasy_score) for user in users]


@app.post("/api/admin/races/{race_id}/results")
def save_results(
    race_id: int,
    payload: RaceResultsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")

    db.query(RaceResult).filter(RaceResult.race_id == race_id).delete()
    for result in payload.results:
        db.add(
            RaceResult(
                race_id=race_id,
                result_type=result.result_type,
                position=result.position,
                driver_id=result.driver_id,
                team_id=result.team_id,
                points=result.points,
            )
        )
    race.status = payload.status
    db.commit()
    return {"saved": len(payload.results), "race_status": race.status}


@app.post("/api/admin/races/{race_id}/score")
def score_results(race_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scored = score_race(db, race_id)
    return {"scored_predictions": scored}


@app.post("/api/assistant/advice", response_model=AssistantResponse)
def assistant_advice(payload: AssistantRequest, current_user: User = Depends(get_current_user)):
    try:
        response = httpx.post(f"{AI_ASSISTANT_URL}/advice", json=payload.dict(), timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return AssistantResponse(
            advice="The assistant service is unavailable. Use recent form, qualifying position, and team pace to make a conservative pick.",
            model_enabled=False,
        )

