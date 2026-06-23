from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nickname = Column(String(80), unique=True, nullable=False, index=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(String(40), nullable=False, default="free")
    credit_balance = Column(Numeric(10, 2), nullable=False, default=1000)
    fantasy_score = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(40), nullable=False, default="active")

    payment_profiles = relationship("PaymentProfile", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")


class PaymentProfile(Base):
    __tablename__ = "payment_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_customer_id = Column(String(120), nullable=False)
    payment_brand = Column(String(40), nullable=False)
    payment_last4 = Column(String(4), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="payment_profiles")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    short_name = Column(String(40), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    drivers = relationship("Driver", back_populates="team")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    driver_code = Column(String(8), unique=True, nullable=False, index=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    image_url = Column(String(800))
    active = Column(Boolean, nullable=False, default=True)

    team = relationship("Team", back_populates="drivers")


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (UniqueConstraint("season", "round", name="uq_races_season_round"),)

    id = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    race_name = Column(String(160), nullable=False)
    circuit_name = Column(String(160), nullable=False)
    country = Column(String(120), nullable=False)
    race_date = Column(Date, nullable=False)
    thumbnail_url = Column(String(800))
    status = Column(String(40), nullable=False, default="scheduled")

    predictions = relationship("Prediction", back_populates="race")
    results = relationship("RaceResult", back_populates="race")


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("user_id", "race_id", name="uq_predictions_user_race"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False, index=True)
    stake_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(40), nullable=False, default="submitted")
    score = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    locked_at = Column(DateTime)

    user = relationship("User", back_populates="predictions")
    race = relationship("Race", back_populates="predictions")
    items = relationship("PredictionItem", back_populates="prediction", cascade="all, delete-orphan")


class PredictionItem(Base):
    __tablename__ = "prediction_items"

    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)
    prediction_type = Column(String(40), nullable=False, index=True)
    position = Column(Integer)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    points_awarded = Column(Integer, nullable=False, default=0)

    prediction = relationship("Prediction", back_populates="items")
    driver = relationship("Driver")
    team = relationship("Team")


class RaceResult(Base):
    __tablename__ = "race_results"

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False, index=True)
    result_type = Column(String(40), nullable=False, index=True)
    position = Column(Integer)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    points = Column(Integer, nullable=False, default=0)

    race = relationship("Race", back_populates="results")
    driver = relationship("Driver")
    team = relationship("Team")
