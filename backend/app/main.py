"""Creates the FastAPI application object that the server runs."""

import logging

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings

# Print the app's own log lines (info and above) with time, level and module name.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
# httpx logs every request at info level; keep only its warnings and errors.
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
)
app.include_router(api_router, prefix="/api/v1")
