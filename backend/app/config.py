import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./formula_fantasy.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")
JWT_ALGORITHM = "HS256"
AI_ASSISTANT_URL = os.getenv("AI_ASSISTANT_URL", "http://localhost:8001")

