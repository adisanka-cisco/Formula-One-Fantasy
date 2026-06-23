from datetime import date, datetime
from decimal import Decimal
from urllib.parse import quote

from .auth import hash_password
from .db import SessionLocal
from .models import Driver, PaymentProfile, Prediction, PredictionItem, Race, RaceResult, Team, User
from .scoring import score_race


TEAM_COLORS = {
    "MCL": "#ff8700",
    "FER": "#d71920",
    "RBR": "#203b78",
    "MER": "#00a19b",
    "AMR": "#00665e",
    "ALP": "#2293d1",
    "HAA": "#b6babd",
    "VRB": "#2b4562",
    "WIL": "#00a3e0",
    "AUD": "#38d430",
    "CAD": "#1f2937",
}


TEAMS = [
    ("McLaren", "MCL"),
    ("Ferrari", "FER"),
    ("Red Bull Racing", "RBR"),
    ("Mercedes", "MER"),
    ("Aston Martin", "AMR"),
    ("Alpine", "ALP"),
    ("Haas", "HAA"),
    ("Racing Bulls", "VRB"),
    ("Williams", "WIL"),
    ("Audi", "AUD"),
    ("Cadillac", "CAD"),
]


DRIVERS = [
    ("NOR", "Lando", "Norris", "MCL"),
    ("PIA", "Oscar", "Piastri", "MCL"),
    ("LEC", "Charles", "Leclerc", "FER"),
    ("HAM", "Lewis", "Hamilton", "FER"),
    ("VER", "Max", "Verstappen", "RBR"),
    ("HAD", "Isack", "Hadjar", "RBR"),
    ("RUS", "George", "Russell", "MER"),
    ("ANT", "Kimi", "Antonelli", "MER"),
    ("ALO", "Fernando", "Alonso", "AMR"),
    ("STR", "Lance", "Stroll", "AMR"),
    ("GAS", "Pierre", "Gasly", "ALP"),
    ("COL", "Franco", "Colapinto", "ALP"),
    ("OCO", "Esteban", "Ocon", "HAA"),
    ("BEA", "Oliver", "Bearman", "HAA"),
    ("LAW", "Liam", "Lawson", "VRB"),
    ("LIN", "Arvid", "Lindblad", "VRB"),
    ("ALB", "Alex", "Albon", "WIL"),
    ("SAI", "Carlos", "Sainz", "WIL"),
    ("HUL", "Nico", "Hulkenberg", "AUD"),
    ("BOR", "Gabriel", "Bortoleto", "AUD"),
    ("PER", "Sergio", "Perez", "CAD"),
    ("BOT", "Valtteri", "Bottas", "CAD"),
]


RACES = [
    (2026, 1, "Australian Grand Prix", "Albert Park Circuit", "Australia", date(2026, 3, 8), "scored"),
    (2026, 2, "Chinese Grand Prix", "Shanghai International Circuit", "China", date(2026, 3, 15), "scored"),
    (2026, 3, "Japanese Grand Prix", "Suzuka Circuit", "Japan", date(2026, 3, 29), "scored"),
    (2026, 4, "Miami Grand Prix", "Miami International Autodrome", "United States", date(2026, 5, 3), "scored"),
    (2026, 5, "Canadian Grand Prix", "Circuit Gilles-Villeneuve", "Canada", date(2026, 5, 24), "scored"),
    (2026, 6, "Monaco Grand Prix", "Circuit de Monaco", "Monaco", date(2026, 6, 7), "scored"),
    (2026, 7, "Barcelona-Catalunya Grand Prix", "Circuit de Barcelona-Catalunya", "Spain", date(2026, 6, 14), "scored"),
    (2026, 8, "Austrian Grand Prix", "Red Bull Ring", "Austria", date(2026, 6, 28), "open_for_predictions"),
    (2026, 9, "British Grand Prix", "Silverstone Circuit", "Great Britain", date(2026, 7, 5), "scheduled"),
    (2026, 10, "Belgian Grand Prix", "Circuit de Spa-Francorchamps", "Belgium", date(2026, 7, 19), "scheduled"),
    (2026, 11, "Hungarian Grand Prix", "Hungaroring", "Hungary", date(2026, 7, 26), "scheduled"),
    (2026, 12, "Dutch Grand Prix", "Circuit Zandvoort", "Netherlands", date(2026, 8, 23), "scheduled"),
    (2026, 13, "Italian Grand Prix", "Monza Autodromo", "Italy", date(2026, 9, 6), "scheduled"),
    (2026, 14, "Spanish Grand Prix", "Madring Circuit", "Spain", date(2026, 9, 13), "scheduled"),
    (2026, 15, "Azerbaijan Grand Prix", "Baku City Circuit", "Azerbaijan", date(2026, 9, 26), "scheduled"),
    (2026, 16, "Singapore Grand Prix", "Marina Bay Street Circuit", "Singapore", date(2026, 10, 11), "scheduled"),
    (2026, 17, "United States Grand Prix", "Circuit of The Americas", "United States", date(2026, 10, 25), "scheduled"),
    (2026, 18, "Mexico City Grand Prix", "Autodromo Hermanos Rodriguez", "Mexico", date(2026, 11, 1), "scheduled"),
    (2026, 19, "Sao Paulo Grand Prix", "Interlagos Circuit", "Brazil", date(2026, 11, 8), "scheduled"),
    (2026, 20, "Las Vegas Grand Prix", "Las Vegas Strip Circuit", "United States", date(2026, 11, 21), "scheduled"),
    (2026, 21, "Qatar Grand Prix", "Lusail International Circuit", "Qatar", date(2026, 11, 29), "scheduled"),
    (2026, 22, "Abu Dhabi Grand Prix", "Yas Marina Circuit", "United Arab Emirates", date(2026, 12, 6), "scheduled"),
]


DEMO_USERS = [
    ("apexamy", "Amy", "Apex"),
    ("brakeben", "Ben", "Brake"),
    ("chicanecam", "Cam", "Chicane"),
    ("drsdan", "Dan", "DRS"),
    ("eaurougeeva", "Eva", "Rouge"),
    ("fastfiona", "Fiona", "Fast"),
    ("gridgeorge", "George", "Grid"),
    ("hairpinhana", "Hana", "Hairpin"),
    ("insideian", "Ian", "Inside"),
    ("jumpstartjo", "Jo", "Jumpstart"),
    ("kerbkara", "Kara", "Kerb"),
    ("lapliam", "Liam", "Lap"),
    ("marblesmia", "Mia", "Marbles"),
    ("nurbnick", "Nick", "Nurb"),
    ("overcutomar", "Omar", "Overcut"),
    ("pitpaula", "Paula", "Pit"),
    ("qualyquinn", "Quinn", "Qualy"),
    ("racingrita", "Rita", "Racing"),
    ("sectorsean", "Sean", "Sector"),
    ("towtina", "Tina", "Tow"),
]


RESULT_WINNERS = ["RUS", "ANT", "ANT", "ANT", "ANT", "ANT", "HAM"]
PODIUM_SECOND = ["ANT", "RUS", "PIA", "NOR", "HAM", "HAM", "RUS"]
PODIUM_THIRD = ["LEC", "HAM", "LEC", "PIA", "VER", "GAS", "NOR"]


def svg_data_uri(svg):
    return "data:image/svg+xml;utf8," + quote(svg)


def driver_avatar(code, first_name, last_name, team_short):
    color = TEAM_COLORS[team_short]
    initials = f"{first_name[0]}{last_name[0]}"
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
      <rect width="96" height="96" rx="20" fill="#101820"/>
      <circle cx="48" cy="35" r="18" fill="{color}"/>
      <path d="M18 86c4-20 16-30 30-30s26 10 30 30" fill="{color}" opacity=".75"/>
      <text x="48" y="53" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#fff">{initials}</text>
      <text x="48" y="82" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#fff">{code}</text>
    </svg>
    """
    return svg_data_uri(svg)


def circuit_thumbnail(round_number, race_name, circuit_name):
    hue = (round_number * 31) % 360
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="hsl({hue},70%,34%)"/>
          <stop offset="1" stop-color="#111827"/>
        </linearGradient>
      </defs>
      <rect width="320" height="180" fill="url(#g)"/>
      <path d="M38 113 C68 46, 132 38, 166 72 S238 126, 280 72" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round"/>
      <path d="M38 113 C68 46, 132 38, 166 72 S238 126, 280 72" fill="none" stroke="#d71920" stroke-width="4" stroke-linecap="round"/>
      <circle cx="38" cy="113" r="8" fill="#fff"/>
      <text x="22" y="34" font-family="Arial" font-size="18" font-weight="700" fill="#fff">R{round_number}</text>
      <text x="22" y="154" font-family="Arial" font-size="20" font-weight="700" fill="#fff">{race_name}</text>
      <text x="22" y="174" font-family="Arial" font-size="12" fill="#dbeafe">{circuit_name}</text>
    </svg>
    """
    return svg_data_uri(svg)


def get_or_create_user(db, nickname, first_name, last_name, password_hash, subscription_tier="free"):
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        user = User(
            nickname=nickname,
            first_name=first_name,
            last_name=last_name,
            email=f"{nickname}@example.com",
            password_hash=password_hash,
            subscription_tier=subscription_tier,
            credit_balance=Decimal("1000"),
            status="active",
        )
        db.add(user)
        db.flush()
    return user


def seed_results(db, race_by_round, driver_by_code, team_by_short):
    for index, winner_code in enumerate(RESULT_WINNERS):
        race = race_by_round[index + 1]
        existing = db.query(RaceResult).filter(RaceResult.race_id == race.id).first()
        if existing:
            continue

        ordered_codes = [
            winner_code,
            PODIUM_SECOND[index],
            PODIUM_THIRD[index],
            "NOR",
            "PIA",
            "VER",
            "LEC",
            "RUS",
            "HAM",
            "ALO",
        ]
        seen = set()
        finishing_order = []
        for code in ordered_codes + [code for code, *_ in DRIVERS]:
            if code not in seen:
                finishing_order.append(code)
                seen.add(code)
            if len(finishing_order) == 10:
                break

        for position, code in enumerate(finishing_order, start=1):
            db.add(
                RaceResult(
                    race_id=race.id,
                    result_type="finishing_order",
                    position=position,
                    driver_id=driver_by_code[code].id,
                    points=0,
                )
            )

        winner_team = driver_by_code[winner_code].team
        pit_team = team_by_short["MCL" if index % 2 == 0 else "RBR"]
        driver_of_day = driver_by_code[PODIUM_THIRD[index]]
        db.add(RaceResult(race_id=race.id, result_type="constructor_points", team_id=winner_team.id, points=25))
        db.add(RaceResult(race_id=race.id, result_type="fastest_pit_stop", team_id=pit_team.id, points=0))
        db.add(RaceResult(race_id=race.id, result_type="driver_of_the_day", driver_id=driver_of_day.id, points=0))


def prediction_items_for(user_index, race, drivers, teams):
    offset = (user_index + race.round) % len(drivers)
    ordered_drivers = drivers[offset:] + drivers[:offset]
    top_10 = ordered_drivers[:10]
    winner = top_10[0]
    podium = top_10[:3]
    top_team = teams[(user_index + race.round) % len(teams)]
    pit_team = teams[(user_index + race.round + 3) % len(teams)]
    dotd = top_10[(user_index + 2) % len(top_10)]

    items = [PredictionItem(prediction_type="race_winner", position=1, driver_id=winner.id)]
    items.extend(PredictionItem(prediction_type="podium", position=index + 1, driver_id=driver.id) for index, driver in enumerate(podium))
    items.extend(PredictionItem(prediction_type="top_10", position=index + 1, driver_id=driver.id) for index, driver in enumerate(top_10))
    items.append(PredictionItem(prediction_type="top_team", team_id=top_team.id))
    items.append(PredictionItem(prediction_type="fastest_pit_stop", team_id=pit_team.id))
    items.append(PredictionItem(prediction_type="driver_of_the_day", driver_id=dotd.id))
    return items


def seed_predictions(db, users, races, drivers, teams):
    for user_index, user in enumerate(users):
        for race in races:
            prediction = db.query(Prediction).filter(Prediction.user_id == user.id, Prediction.race_id == race.id).first()
            if not prediction:
                prediction = Prediction(
                    user_id=user.id,
                    race_id=race.id,
                    stake_amount=Decimal(str(10 + ((user_index + race.round) % 5) * 5)),
                    status="submitted",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(prediction)
                db.flush()
                prediction.items = prediction_items_for(user_index, race, drivers, teams)


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
            team.name = name
            team.active = True
            team_by_short[short_name] = team

        driver_by_code = {}
        for code, first_name, last_name, short_name in DRIVERS:
            driver = db.query(Driver).filter(Driver.driver_code == code).first()
            if not driver:
                driver = Driver(driver_code=code, first_name=first_name, last_name=last_name, team_id=team_by_short[short_name].id)
                db.add(driver)
                db.flush()
            driver.first_name = first_name
            driver.last_name = last_name
            driver.team_id = team_by_short[short_name].id
            driver.image_url = driver_avatar(code, first_name, last_name, short_name)
            driver.active = True
            driver_by_code[code] = driver

        active_driver_codes = [code for code, *_ in DRIVERS]
        db.query(Driver).filter(~Driver.driver_code.in_(active_driver_codes)).update({Driver.active: False}, synchronize_session=False)

        race_by_round = {}
        for season, round_number, name, circuit, country, race_date, status in RACES:
            race = db.query(Race).filter(Race.season == season, Race.round == round_number).first()
            if not race:
                race = Race(
                    season=season,
                    round=round_number,
                    race_name=name,
                    circuit_name=circuit,
                    country=country,
                    race_date=race_date,
                    status=status,
                )
                db.add(race)
                db.flush()
            race.race_name = name
            race.circuit_name = circuit
            race.country = country
            race.race_date = race_date
            race.thumbnail_url = circuit_thumbnail(round_number, name, circuit)
            if race.status not in {"scored", "completed"}:
                race.status = status
            race_by_round[round_number] = race

        demo_hash = hash_password("DemoPass123")
        demo_users = [
            get_or_create_user(db, nickname, first_name, last_name, demo_hash, "free")
            for nickname, first_name, last_name in DEMO_USERS
        ]
        get_or_create_user(db, "cisco", "Cisco", "Demo", hash_password("C1sco12345"), "premium")

        for index, user in enumerate(demo_users):
            if not db.query(PaymentProfile).filter(PaymentProfile.user_id == user.id).first():
                db.add(
                    PaymentProfile(
                        user_id=user.id,
                        payment_customer_id=f"demo-customer-{user.nickname}",
                        payment_brand=["Visa", "Mastercard", "Amex"][index % 3],
                        payment_last4=f"{4100 + index}"[-4:],
                    )
                )

        db.commit()

        drivers = [driver_by_code[code] for code, *_ in DRIVERS]
        teams = [team_by_short[short_name] for _, short_name in TEAMS]
        races = [race_by_round[round_number] for round_number in sorted(race_by_round)]

        seed_results(db, race_by_round, driver_by_code, team_by_short)
        seed_predictions(db, demo_users, races, drivers, teams)
        db.commit()

        for race_round in range(1, len(RESULT_WINNERS) + 1):
            score_race(db, race_by_round[race_round].id)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
