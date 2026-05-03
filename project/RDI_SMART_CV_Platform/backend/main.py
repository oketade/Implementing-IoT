import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base
from routers import cv, profile, ai

# Auto-create tables on startup (for dev/SQLite; use Alembic migrations in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RDI Smart CV Platform API",
    version="1.0.0",
    description="AI-powered CV parsing, enhancement, and profile management.",
)

# CORS — allow any localhost port (dev) plus configured frontend URL
_frontend_url = os.getenv("FRONTEND_URL", "").strip()
origins = list(filter(None, [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3005",
    "http://localhost:3006",
    _frontend_url,
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router, tags=["CV"])
app.include_router(profile.router, tags=["Profile"])
app.include_router(ai.router, tags=["AI"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "RDI Smart CV API"}
