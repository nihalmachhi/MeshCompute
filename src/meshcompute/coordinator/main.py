"""Coordinator FastAPI app factory and lifecycle wiring."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from meshcompute.coordinator.api import (
    routes_jobs,
    routes_metrics,
    routes_tasks,
    routes_workers,
    ws_events,
)
from meshcompute.coordinator.background.lease_reaper import run_reaper
from meshcompute.coordinator.background.outbox_dispatcher import run_outbox_dispatcher
from meshcompute.coordinator.background.purger import run_purger
from meshcompute.core.errors import (
    BackpressureError,
    ConflictError,
    MeshComputeError,
    NotFoundError,
    PayloadTooLargeError,
)
from meshcompute.core.logging import configure_logging
from meshcompute.core.settings import get_settings


def create_app() -> FastAPI:
    """Build the HTTP application with explicit startup and shutdown resources."""
    settings = get_settings()
    configure_logging(settings.log_level)
    stop = asyncio.Event()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        reaper = asyncio.create_task(run_reaper(stop))
        dispatcher = asyncio.create_task(run_outbox_dispatcher(stop))
        purger = asyncio.create_task(run_purger(stop))
        yield
        stop.set()
        await asyncio.gather(reaper, dispatcher, purger)

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(routes_jobs.router, prefix="/api/v1")
    app.include_router(routes_workers.router, prefix="/api/v1")
    app.include_router(routes_tasks.router, prefix="/api/v1")
    app.include_router(routes_metrics.router, prefix="/api/v1")
    app.include_router(ws_events.router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Expose process liveness for Compose health checks."""
        return {"status": "ok", "service": "coordinator"}

    @app.exception_handler(MeshComputeError)
    async def handle_domain_error(request: Request, exc: MeshComputeError):
        """Translate expected domain failures into stable API responses."""
        status = (
            413
            if isinstance(exc, PayloadTooLargeError)
            else 404
            if isinstance(exc, NotFoundError)
            else 429
            if isinstance(exc, BackpressureError)
            else 409
            if isinstance(exc, ConflictError)
            else 400
        )
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return app


# app instance is created via factory (--factory) to avoid import-time side effects
