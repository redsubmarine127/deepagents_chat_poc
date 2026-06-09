from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import create_api_router
from app.config import get_settings
from app.observability import configure_app_logging
from app.runtime import build_runtime

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app() -> FastAPI:
    configure_app_logging()
    settings = get_settings()
    runtime = build_runtime(settings, PROJECT_ROOT)

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(
        create_api_router(
            runtime.repository,
            runtime.chat_service,
            runtime.skills,
            runtime.tool_catalog.metadata,
            runtime.approval_store,
        )
    )
    return app


app = create_app()
