from fastapi import FastAPI

from app.logging import get_logger, setup_logging

setup_logging()
log = get_logger()

app = FastAPI(title="Trello Clone API", version="0.1.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    log.info("health_check", status="ok")
    return {"status": "ok"}
