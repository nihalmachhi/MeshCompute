"""FastAPI dependencies for transaction scopes and shared event publication."""
from collections.abc import Generator
from meshcompute.coordinator.db.unit_of_work import UnitOfWork

def get_uow() -> Generator[UnitOfWork,None,None]:
    """Provide one transaction-scoped unit of work per HTTP request."""
    with UnitOfWork() as uow:yield uow
