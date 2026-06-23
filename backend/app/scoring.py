from typing import Dict, List, Optional, Set

from sqlalchemy.orm import Session

from .models import Prediction, PredictionItem, Race, RaceResult, User


PREDICTION_TYPES = {
    "race_winner",
    "podium",
    "top_10",
    "top_team",
    "fastest_pit_stop",
    "driver_of_the_day",
}


def _result_by_type(results: List[RaceResult], result_type: str) -> List[RaceResult]:
    return [result for result in results if result.result_type == result_type]


def _driver_at(results: List[RaceResult], position: int) -> Optional[int]:
    for result in results:
        if result.position == position:
            return result.driver_id
    return None


def _driver_set(results: List[RaceResult], max_position: int) -> Set[int]:
    return {result.driver_id for result in results if result.driver_id and result.position and result.position <= max_position}


def _team_result(results: List[RaceResult], result_type: str) -> Optional[int]:
    matches = _result_by_type(results, result_type)
    return matches[0].team_id if matches else None


def _driver_result(results: List[RaceResult], result_type: str) -> Optional[int]:
    matches = _result_by_type(results, result_type)
    return matches[0].driver_id if matches else None


def score_prediction(prediction: Prediction, results: List[RaceResult]) -> int:
    finishing = _result_by_type(results, "finishing_order")
    top_3 = _driver_set(finishing, 3)
    top_10 = _driver_set(finishing, 10)
    winner_id = _driver_at(finishing, 1)
    top_team_id = _team_result(results, "constructor_points")
    fastest_pit_team_id = _team_result(results, "fastest_pit_stop")
    driver_of_day_id = _driver_result(results, "driver_of_the_day")

    total = 0
    for item in prediction.items:
        points = 0
        if item.prediction_type == "race_winner" and item.driver_id == winner_id:
            points = 25
        elif item.prediction_type == "podium" and item.driver_id in top_3:
            points = 10
            if item.position and item.driver_id == _driver_at(finishing, item.position):
                points += 5
        elif item.prediction_type == "top_10" and item.driver_id in top_10:
            points = 2
            if item.position and item.driver_id == _driver_at(finishing, item.position):
                points += 3
        elif item.prediction_type == "top_team" and item.team_id == top_team_id:
            points = 15
        elif item.prediction_type == "fastest_pit_stop" and item.team_id == fastest_pit_team_id:
            points = 10
        elif item.prediction_type == "driver_of_the_day" and item.driver_id == driver_of_day_id:
            points = 10

        item.points_awarded = points
        total += points

    prediction.score = total
    prediction.status = "scored"
    return total


def score_race(db: Session, race_id: int) -> int:
    race = db.query(Race).filter(Race.id == race_id).first()
    if not race:
        return 0

    results = db.query(RaceResult).filter(RaceResult.race_id == race_id).all()
    predictions = db.query(Prediction).filter(Prediction.race_id == race_id).all()
    scored_count = 0

    for prediction in predictions:
        score_prediction(prediction, results)
        scored_count += 1

    users = db.query(User).all()
    for user in users:
        user.fantasy_score = sum(prediction.score for prediction in user.predictions if prediction.status == "scored")

    race.status = "scored"
    db.commit()
    return scored_count

