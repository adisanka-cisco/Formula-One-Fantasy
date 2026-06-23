from datetime import date

from .db import SessionLocal
from .models import Driver, Race, Team


TEAMS = [
    ("McLaren", "MCL"),
    ("Ferrari", "FER"),
    ("Red Bull Racing", "RBR"),
    ("Mercedes", "MER"),
    ("Aston Martin", "AMR"),
]

DRIVERS = [
    ("NOR", "Lando", "Norris", "MCL"),
    ("PIA", "Oscar", "Piastri", "MCL"),
    ("LEC", "Charles", "Leclerc", "FER"),
    ("HAM", "Lewis", "Hamilton", "FER"),
    ("VER", "Max", "Verstappen", "RBR"),
    ("TSU", "Yuki", "Tsunoda", "RBR"),
    ("RUS", "George", "Russell", "MER"),
    ("ANT", "Kimi", "Antonelli", "MER"),
    ("ALO", "Fernando", "Alonso", "AMR"),
    ("STR", "Lance", "Stroll", "AMR"),
]

RACES = [
    (2026, 1, "Australian Grand Prix", "Albert Park Circuit", "Australia", date(2026, 3, 8), "open_for_predictions"),
    (2026, 2, "Chinese Grand Prix", "Shanghai International Circuit", "China", date(2026, 3, 15), "scheduled"),
    (2026, 3, "Japanese Grand Prix", "Suzuka Circuit", "Japan", date(2026, 3, 29), "scheduled"),
]


def seed():
    db = SessionLocal()
    try:
        team_by_short = {}
        for name, short_name in TEAMS:
            team = db.query(Team).filter(Team.short_name == short_name).first()
            if not team:
                team = Team(name=name, short_name=short_name)
                db.add(team)
                db.flush()
            team_by_short[short_name] = team

        for code, first_name, last_name, short_name in DRIVERS:
            if not db.query(Driver).filter(Driver.driver_code == code).first():
                db.add(Driver(driver_code=code, first_name=first_name, last_name=last_name, team_id=team_by_short[short_name].id))

        for season, round_number, name, circuit, country, race_date, status in RACES:
            if not db.query(Race).filter(Race.season == season, Race.round == round_number).first():
                db.add(
                    Race(
                        season=season,
                        round=round_number,
                        race_name=name,
                        circuit_name=circuit,
                        country=country,
                        race_date=race_date,
                        status=status,
                    )
                )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

