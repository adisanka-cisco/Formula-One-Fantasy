# Formula One Fantasy

A simple Formula One fantasy prediction app for a two-node Kubernetes lab.

The foundation includes:

- React frontend served by Apache httpd
- Python FastAPI backend API
- Placeholder AI assistant service
- Scoring worker
- PostgreSQL schema with 8 application tables
- CloudNativePG manifests for a two-instance Postgres cluster
- k3s deployment notes for `app1` and `app2`

This project is intentionally simple and readable so it can be used as a security-observability demo later with Cilium/Isovalent.

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

AI assistant:

```bash
cd ai-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Kubernetes

See [docs/k3s-lab.md](docs/k3s-lab.md) for the two-node lab setup and deployment flow.

