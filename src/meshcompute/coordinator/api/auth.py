"""Authentication helpers for workers and administrators."""

import hashlib
import secrets

from fastapi import Header, HTTPException

from meshcompute.core.settings import get_settings


def _hash(token: str) -> str:
    """Return a one-way digest for a worker bearer token."""
    return hashlib.sha256(token.encode()).hexdigest()


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """Require a configured admin bearer token; fail closed if missing."""
    settings = get_settings()
    if not settings.admin_token:
        raise HTTPException(status_code=503, detail="admin token is not configured")
    expected = f"Bearer {settings.admin_token}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="admin authentication required")


def extract_worker_token(authorization: str | None = Header(default=None)) -> str | None:
    """Return a bearer token only when the authorization scheme is exact."""
    if authorization is None:
        return None
    scheme, separator, value = authorization.partition(" ")
    token = value.strip()
    return token if separator and scheme.lower() == "bearer" and token else None


def verify_worker(uow, worker_id, authorization: str | None) -> None:
    """Require the issued token to match the active worker identity."""
    token = extract_worker_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="worker authentication required")
    from meshcompute.coordinator.repositories.worker_repo import WorkerRepository

    worker = WorkerRepository(uow.session).get_by_token_hash(_hash(token))
    if worker is None or worker.id != worker_id:
        raise HTTPException(status_code=403, detail="invalid worker token")
    if worker.status != "ACTIVE":
        raise HTTPException(status_code=403, detail="worker is not active")
