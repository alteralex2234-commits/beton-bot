from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import build_api_router
from app.core.container import ServiceContainer


def create_api_app(container: ServiceContainer) -> FastAPI:
    app = FastAPI(title="concrete_bot API", version="1.0.0")
    app.state.services = container
    app.include_router(build_api_router())
    return app
