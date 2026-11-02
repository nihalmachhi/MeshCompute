"""Liveness and database readiness intentionally report different conditions."""

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from meshcompute.coordinator import main
from meshcompute.coordinator.main import create_app


class SessionStub:
    def __init__(self, error: Exception | None = None):
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement):
        if self.error is not None:
            raise self.error
        return 1


def test_health_is_live_when_database_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        main,
        "session_factory",
        lambda: lambda: SessionStub(OperationalError("SELECT 1", {}, RuntimeError("offline"))),
    )
    client = TestClient(create_app())

    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 503


def test_ready_checks_database(monkeypatch):
    monkeypatch.setattr(main, "session_factory", lambda: lambda: SessionStub())
    response = TestClient(create_app()).get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "coordinator"}
