import time

from .db import SessionLocal
from .models import Race
from .scoring import score_race


def run_once() -> int:
    db = SessionLocal()
    try:
        races = db.query(Race).filter(Race.status == "completed").all()
        for race in races:
            score_race(db, race.id)
        return len(races)
    finally:
        db.close()


def run_forever():
    while True:
        run_once()
        time.sleep(30)


if __name__ == "__main__":
    run_forever()

