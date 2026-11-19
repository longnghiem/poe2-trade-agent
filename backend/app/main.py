"""Creates the FastAPI application object that the server runs."""

from fastapi import FastAPI

from app.api.main import api_router

app = FastAPI(
    title="poe2-trade-agent",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
)
app.include_router(api_router, prefix="/api/v1")