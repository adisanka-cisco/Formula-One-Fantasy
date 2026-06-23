from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=2, max_length=80)
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    subscription_tier: str = "free"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nickname: str
    first_name: str
    last_name: str
    email: EmailStr
    subscription_tier: str
    credit_balance: Decimal
    fantasy_score: int
    created_at: datetime
    last_activity_at: datetime
    status: str

    class Config:
        orm_mode = True


class TeamResponse(BaseModel):
    id: int
    name: str
    short_name: str
    active: bool

    class Config:
        orm_mode = True


class DriverResponse(BaseModel):
    id: int
    team_id: int
    driver_code: str
    first_name: str
    last_name: str
    image_url: Optional[str] = None
    active: bool

    class Config:
        orm_mode = True


class RaceResponse(BaseModel):
    id: int
    season: int
    round: int
    race_name: str
    circuit_name: str
    country: str
    race_date: date
    thumbnail_url: Optional[str] = None
    status: str

    class Config:
        orm_mode = True


class PredictionItemIn(BaseModel):
    prediction_type: str
    position: Optional[int] = None
    driver_id: Optional[int] = None
    team_id: Optional[int] = None


class PredictionCreate(BaseModel):
    race_id: int
    stake_amount: Decimal = Decimal("0")
    items: List[PredictionItemIn]


class PredictionItemOut(PredictionItemIn):
    id: int
    points_awarded: int

    class Config:
        orm_mode = True


class PredictionResponse(BaseModel):
    id: int
    user_id: int
    race_id: int
    stake_amount: Decimal
    status: str
    score: int
    created_at: datetime
    updated_at: datetime
    locked_at: Optional[datetime]
    items: List[PredictionItemOut]

    class Config:
        orm_mode = True


class RaceResultIn(BaseModel):
    result_type: str
    position: Optional[int] = None
    driver_id: Optional[int] = None
    team_id: Optional[int] = None
    points: int = 0


class RaceResultsRequest(BaseModel):
    status: str = "completed"
    results: List[RaceResultIn]


class LeaderboardEntry(BaseModel):
    user_id: int
    nickname: str
    fantasy_score: int


class AssistantRequest(BaseModel):
    race_id: int
    question: str
    current_prediction: Dict[str, Any] = {}


class AssistantResponse(BaseModel):
    advice: str
    model_enabled: bool
