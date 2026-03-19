"""FastAPI application entry point for the Trello Clone API."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Database
from app.logging import get_logger, setup_logging
from app.routers.boards import router as boards_router
from app.routers.lists import router as lists_router

setup_logging()
log = get_logger()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage database lifecycle: connect on startup, close on shutdown."""
    db_path = os.environ.get("DB_PATH", "data/trello.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    db = Database(db_path)
    await db.connect()
    await db.init_schema()
    await db.seed_default_board()
    application.state.db = db
    log.info("app_startup_complete", db_path=db_path)
    yield
    await application.state.db.close()
    log.info("app_shutdown_complete")


app = FastAPI(title="Trello Clone API", version="0.1.0", lifespan=lifespan)

# CORS middleware configuration
cors_origins_env = os.environ.get("CORS_ORIGINS")
if cors_origins_env:
    cors_origins: list[str] = [o.strip() for o in cors_origins_env.split(",")]
else:
    cors_origins = ["*"]

log.info("cors_configured", origins=cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boards_router, prefix="/api")
log.info("router_registered", router="boards", prefix="/api")
app.include_router(lists_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict[str, str]:
    log.info("health_check", status="ok")
    return {"status": "ok", "version": "0.1.0"}
