from backend.app.models import Driver, Prediction, PredictionItem, RaceResult, Team
from backend.app.scoring import score_prediction


def test_scores_all_prediction_types():
    team = Team(id=1, name="McLaren", short_name="MCL")
    red_bull = Team(id=2, name="Red Bull Racing", short_name="RBR")
    norris = Driver(id=1, driver_code="NOR", first_name="Lando", last_name="Norris", team=team)
    piastri = Driver(id=2, driver_code="PIA", first_name="Oscar", last_name="Piastri", team=team)
    verstappen = Driver(id=3, driver_code="VER", first_name="Max", last_name="Verstappen", team=red_bull)

    prediction = Prediction(items=[
        PredictionItem(prediction_type="race_winner", position=1, driver_id=norris.id),
        PredictionItem(prediction_type="podium", position=2, driver_id=piastri.id),
        PredictionItem(prediction_type="top_10", position=3, driver_id=verstappen.id),
        PredictionItem(prediction_type="top_team", team_id=team.id),
        PredictionItem(prediction_type="fastest_pit_stop", team_id=red_bull.id),
        PredictionItem(prediction_type="driver_of_the_day", driver_id=norris.id),
    ])
    results = [
        RaceResult(result_type="finishing_order", position=1, driver_id=norris.id),
        RaceResult(result_type="finishing_order", position=2, driver_id=piastri.id),
        RaceResult(result_type="finishing_order", position=3, driver_id=verstappen.id),
        RaceResult(result_type="constructor_points", team_id=team.id),
        RaceResult(result_type="fastest_pit_stop", team_id=red_bull.id),
        RaceResult(result_type="driver_of_the_day", driver_id=norris.id),
    ]

    assert score_prediction(prediction, results) == 80
