"""Authentication helpers for workers and administrators."""

import hashlib

from fastapi import Header, HTTPException

from meshcompute.core.settings import get_settings


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_admin(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.admin_token:
        return
    if authorization != f"Bearer {settings.admin_token}":
        raise HTTPException(status_code=401, detail="admin authentication required")


def extract_worker_token(authorization: str | None = Header(default=None)) -> str | None:
    if authorization and authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return None


def verify_worker(uow, worker_id, authorization: str | None) -> None:
    settings = get_settings()
    if not settings.admin_token and not authorization:
        # development mode: allow
        return
    token = extract_worker_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="worker authentication required")
    from meshcompute.coordinator.repositories.worker_repo import WorkerRepository

    worker = WorkerRepository(uow.session).get_by_token_hash(_hash(token))
    if worker is None or worker.id != worker_id:
        raise HTTPException(status_code=403, detail="invalid worker token")
