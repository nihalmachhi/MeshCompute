from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from meshcompute.coordinator.api import auth


def test_admin_auth_fails_closed_when_no_token_is_configured(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(admin_token=None))
    with pytest.raises(HTTPException) as error:
        auth.require_admin(None)
    assert error.value.status_code == 503


def test_worker_auth_fails_closed_without_issued_token(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(admin_token=None))
    with pytest.raises(HTTPException) as error:
        auth.verify_worker(SimpleNamespace(session=None), uuid4(), None)
    assert error.value.status_code == 401


def test_worker_auth_requires_token_owned_by_worker(monkeypatch):
    worker_id = uuid4()
    monkeypatch.setattr(auth, "get_settings", lambda: SimpleNamespace(admin_token="admin"))

    class Session:
        def scalar(self, _statement):
            return SimpleNamespace(id=uuid4())

    with pytest.raises(HTTPException) as error:
        auth.verify_worker(SimpleNamespace(session=Session()), worker_id, "Bearer issued")
    assert error.value.status_code == 403
