"""Main application entrypoint for TinyFish Job Scraper."""
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.scheduler import scheduler
from app.api import router as api_router

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Start Freshness Scheduler
    init_db()
    scheduler.start()
    yield
    # Shutdown: Stop Scheduler
    scheduler.stop()

app = FastAPI(
    title="TinyFish AI Job & Internship Scraper",
    description="Agentic web scraper pulling live openings from career portals with role, location & seniority matching.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def index_view(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
