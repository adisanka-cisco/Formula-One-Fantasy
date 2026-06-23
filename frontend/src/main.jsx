import React, { useEffect, useMemo, useState } from "react";
import { render } from "react-dom";
import "./styles.css";

const API_BASE = "";

function apiFetch(path, options = {}, token = "") {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers }).then(async (response) => {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }
    return data;
  });
}

function App() {
  const [token, setToken] = useState(localStorage.getItem("formula_token") || "");
  const [me, setMe] = useState(null);
  const [races, setRaces] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [selectedRaceId, setSelectedRaceId] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadPublicData();
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem("formula_token", token);
      apiFetch("/api/me", {}, token).then(setMe).catch(() => logout());
    }
  }, [token]);

  const selectedRace = useMemo(
    () => races.find((race) => String(race.id) === String(selectedRaceId)) || races[0],
    [races, selectedRaceId]
  );

  function loadPublicData() {
    Promise.all([
      apiFetch("/api/races"),
      apiFetch("/api/drivers"),
      apiFetch("/api/teams"),
      apiFetch("/api/leaderboard"),
    ])
      .then(([raceData, driverData, teamData, leaderboardData]) => {
        setRaces(raceData);
        setDrivers(driverData);
        setTeams(teamData);
        setLeaderboard(leaderboardData);
        if (raceData.length && !selectedRaceId) {
          setSelectedRaceId(String(raceData[0].id));
        }
      })
      .catch((error) => setMessage(error.message));
  }

  function logout() {
    localStorage.removeItem("formula_token");
    setToken("");
    setMe(null);
  }

  return (
    <main>
      <section className="hero">
        <img src="/race-control-banner.png" alt="" />
        <div className="heroOverlay">
          <div>
            <p className="eyebrow">Formula One Fantasy</p>
            <h1>Race Predictions</h1>
          </div>
          <div className="profile">
            {me ? (
              <>
                <strong>{me.nickname}</strong>
                <span>{me.fantasy_score} pts</span>
                <button onClick={logout}>Sign out</button>
              </>
            ) : (
              <span>Sign in to submit picks</span>
            )}
          </div>
        </div>
      </section>

      {message && <div className="notice">{message}</div>}

      <section className="layout">
        <aside className="sidebar">
          {me ? <AccountPanel me={me} /> : <AuthPanel setToken={setToken} setMessage={setMessage} />}
          <Leaderboard entries={leaderboard} />
        </aside>

        <section className="workspace">
          <RaceTabs races={races} selectedRaceId={selectedRaceId} setSelectedRaceId={setSelectedRaceId} />
          {selectedRace && (
            <PredictionPanel
              race={selectedRace}
              drivers={drivers}
              teams={teams}
              token={token}
              reload={loadPublicData}
              setMessage={setMessage}
            />
          )}
          <AssistantPanel race={selectedRace} token={token} setMessage={setMessage} />
          <AdminResults race={selectedRace} drivers={drivers} teams={teams} token={token} setMessage={setMessage} reload={loadPublicData} />
        </section>
      </section>
    </main>
  );
}

function AuthPanel({ setToken, setMessage }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    nickname: "racefan",
    first_name: "Race",
    last_name: "Fan",
    email: "racefan@example.com",
    password: "Formula123",
    subscription_tier: "free",
  });

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function submit(event) {
    event.preventDefault();
    const path = mode === "login" ? "/api/auth/login" : "/api/auth/register";
    const body = mode === "login" ? { email: form.email, password: form.password } : form;
    apiFetch(path, { method: "POST", body: JSON.stringify(body) })
      .then((data) => setToken(data.access_token))
      .catch((error) => setMessage(error.message));
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Account</h2>
        <div className="segmented">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
      </div>
      <form onSubmit={submit} className="formGrid">
        {mode === "register" && (
          <>
            <input value={form.nickname} onChange={(event) => update("nickname", event.target.value)} placeholder="Nickname" />
            <input value={form.first_name} onChange={(event) => update("first_name", event.target.value)} placeholder="First name" />
            <input value={form.last_name} onChange={(event) => update("last_name", event.target.value)} placeholder="Last name" />
          </>
        )}
        <input value={form.email} onChange={(event) => update("email", event.target.value)} placeholder="Email" />
        <input value={form.password} onChange={(event) => update("password", event.target.value)} placeholder="Password" type="password" />
        <button type="submit">{mode === "login" ? "Login" : "Create account"}</button>
      </form>
    </section>
  );
}

function AccountPanel({ me }) {
  return (
    <section className="panel stats">
      <h2>Account</h2>
      <div><span>Tier</span><strong>{me.subscription_tier}</strong></div>
      <div><span>Credits</span><strong>{Number(me.credit_balance).toFixed(0)}</strong></div>
      <div><span>Score</span><strong>{me.fantasy_score}</strong></div>
    </section>
  );
}

function Leaderboard({ entries }) {
  return (
    <section className="panel">
      <h2>Leaderboard</h2>
      <ol className="leaderboard">
        {entries.map((entry) => (
          <li key={entry.user_id}>
            <span>{entry.nickname}</span>
            <strong>{entry.fantasy_score}</strong>
          </li>
        ))}
        {!entries.length && <li>No scores yet</li>}
      </ol>
    </section>
  );
}

function RaceTabs({ races, selectedRaceId, setSelectedRaceId }) {
  return (
    <section className="raceStrip">
      {races.map((race) => (
        <button
          key={race.id}
          className={String(race.id) === String(selectedRaceId) ? "active" : ""}
          onClick={() => setSelectedRaceId(String(race.id))}
        >
          <span>Round {race.round}</span>
          <strong>{race.race_name}</strong>
        </button>
      ))}
    </section>
  );
}

function PredictionPanel({ race, drivers, teams, token, reload, setMessage }) {
  const driverIds = drivers.map((driver) => String(driver.id));
  const defaultDriver = driverIds[0] || "";
  const defaultTeam = teams[0] ? String(teams[0].id) : "";
  const [winner, setWinner] = useState(defaultDriver);
  const [podium, setPodium] = useState([defaultDriver, driverIds[1] || defaultDriver, driverIds[2] || defaultDriver]);
  const [top10, setTop10] = useState(driverIds.slice(0, 10));
  const [topTeam, setTopTeam] = useState(defaultTeam);
  const [fastestPitStop, setFastestPitStop] = useState(defaultTeam);
  const [driverOfDay, setDriverOfDay] = useState(defaultDriver);

  useEffect(() => {
    setWinner(defaultDriver);
    setPodium([defaultDriver, driverIds[1] || defaultDriver, driverIds[2] || defaultDriver]);
    setTop10(driverIds.slice(0, 10));
    setTopTeam(defaultTeam);
    setFastestPitStop(defaultTeam);
    setDriverOfDay(defaultDriver);
  }, [race.id, drivers.length, teams.length]);

  function driverSelect(value, onChange) {
    return (
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {drivers.map((driver) => (
          <option key={driver.id} value={driver.id}>{driver.driver_code} - {driver.first_name} {driver.last_name}</option>
        ))}
      </select>
    );
  }

  function teamSelect(value, onChange) {
    return (
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
      </select>
    );
  }

  function updateList(list, index, value) {
    return list.map((item, itemIndex) => (itemIndex === index ? value : item));
  }

  function submit() {
    if (!token) {
      setMessage("Login before submitting predictions.");
      return;
    }
    const items = [
      { prediction_type: "race_winner", position: 1, driver_id: Number(winner) },
      ...podium.map((driverId, index) => ({ prediction_type: "podium", position: index + 1, driver_id: Number(driverId) })),
      ...top10.map((driverId, index) => ({ prediction_type: "top_10", position: index + 1, driver_id: Number(driverId) })),
      { prediction_type: "top_team", team_id: Number(topTeam) },
      { prediction_type: "fastest_pit_stop", team_id: Number(fastestPitStop) },
      { prediction_type: "driver_of_the_day", driver_id: Number(driverOfDay) },
    ];
    apiFetch("/api/predictions", {
      method: "POST",
      body: JSON.stringify({ race_id: race.id, stake_amount: 25, items }),
    }, token)
      .then(() => {
        setMessage("Prediction submitted.");
        reload();
      })
      .catch((error) => setMessage(error.message));
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <div>
          <h2>{race.race_name}</h2>
          <p>{race.circuit_name} · {race.country} · {race.status}</p>
        </div>
        <button onClick={submit}>Submit picks</button>
      </div>
      <div className="predictionGrid">
        <label>Race winner {driverSelect(winner, setWinner)}</label>
        <label>Top team {teamSelect(topTeam, setTopTeam)}</label>
        <label>Fastest pit stop {teamSelect(fastestPitStop, setFastestPitStop)}</label>
        <label>Driver of the day {driverSelect(driverOfDay, setDriverOfDay)}</label>
      </div>
      <h3>Podium</h3>
      <div className="positionGrid three">
        {podium.map((driverId, index) => (
          <label key={index}>P{index + 1} {driverSelect(driverId, (value) => setPodium(updateList(podium, index, value)))}</label>
        ))}
      </div>
      <h3>Top 10</h3>
      <div className="positionGrid">
        {top10.map((driverId, index) => (
          <label key={index}>P{index + 1} {driverSelect(driverId, (value) => setTop10(updateList(top10, index, value)))}</label>
        ))}
      </div>
    </section>
  );
}

function AssistantPanel({ race, token, setMessage }) {
  const [question, setQuestion] = useState("Who should I pick for podium?");
  const [advice, setAdvice] = useState("");

  function askAssistant() {
    if (!token) {
      setMessage("Login before using the assistant.");
      return;
    }
    apiFetch("/api/assistant/advice", {
      method: "POST",
      body: JSON.stringify({ race_id: race ? race.id : 1, question, current_prediction: {} }),
    }, token)
      .then((data) => setAdvice(data.advice))
      .catch((error) => setMessage(error.message));
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>AI Assistant</h2>
        <button onClick={askAssistant}>Ask</button>
      </div>
      <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
      {advice && <p className="assistantAnswer">{advice}</p>}
    </section>
  );
}

function AdminResults({ race, drivers, teams, token, setMessage, reload }) {
  const [winnerDriver, setWinnerDriver] = useState("");
  const [topTeam, setTopTeam] = useState("");

  useEffect(() => {
    if (drivers[0]) setWinnerDriver(String(drivers[0].id));
    if (teams[0]) setTopTeam(String(teams[0].id));
  }, [drivers.length, teams.length]);

  function saveAndScore() {
    if (!token || !race) {
      setMessage("Login before saving admin results.");
      return;
    }
    const topDrivers = drivers.slice(0, 10).map((driver, index) => ({
      result_type: "finishing_order",
      position: index + 1,
      driver_id: index === 0 ? Number(winnerDriver) : driver.id,
      points: 0,
    }));
    const results = [
      ...topDrivers,
      { result_type: "constructor_points", team_id: Number(topTeam), points: 25 },
      { result_type: "fastest_pit_stop", team_id: Number(topTeam), points: 0 },
      { result_type: "driver_of_the_day", driver_id: Number(winnerDriver), points: 0 },
    ];
    apiFetch(`/api/admin/races/${race.id}/results`, {
      method: "POST",
      body: JSON.stringify({ status: "completed", results }),
    }, token)
      .then(() => apiFetch(`/api/admin/races/${race.id}/score`, { method: "POST" }, token))
      .then(() => {
        setMessage("Race results saved and scored.");
        reload();
      })
      .catch((error) => setMessage(error.message));
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Admin Results</h2>
        <button onClick={saveAndScore}>Save + score</button>
      </div>
      <div className="predictionGrid">
        <label>Winner
          <select value={winnerDriver} onChange={(event) => setWinnerDriver(event.target.value)}>
            {drivers.map((driver) => <option key={driver.id} value={driver.id}>{driver.driver_code}</option>)}
          </select>
        </label>
        <label>Top constructor
          <select value={topTeam} onChange={(event) => setTopTeam(event.target.value)}>
            {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
          </select>
        </label>
      </div>
    </section>
  );
}

render(<App />, document.getElementById("root"));

