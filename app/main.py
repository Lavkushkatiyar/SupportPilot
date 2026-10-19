import logging

from fastapi import FastAPI

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(api_router)


@app.get(
    "/",
)
async def home_page() -> dict[str, object]:
    logger.info("Ready check requested")
    return {
        "name": "SupportPilot API",
        "description": "An AI-assisted customer support API that classifies"
        "support messages, identifies escalation needs, retrieves "
        "similar historical cases, and drafts replies.",
        "status": "running",
        "documentation": "/docs",
        "health_check": "/health",
        "how_to_use": [
            "Open /docs to explore available endpoints.",
            "Register or log in to obtain authentication credentials.",
            "Authorize requests to protected endpoints.",
            "Submit a support message for classification and processing.",
            "Review the generated draft and escalation result.",
        ],
        "limitations": [
            "Generated replies are drafts, not executed customer-support actions.",
            "Access to protected endpoints requires authorization.",
        ],
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
async def ready_check() -> dict[str, str]:
    logger.info("Ready check requested")
    return {"status": "ready"}
