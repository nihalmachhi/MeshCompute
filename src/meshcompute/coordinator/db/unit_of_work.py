"""Own one database transaction and its repositories per application operation."""

from sqlalchemy.orm import Session

from meshcompute.coordinator.db.session import session_factory
from meshcompute.coordinator.repositories.job_repo import JobRepository
from meshcompute.coordinator.repositories.result_repo import ResultRepository
from meshcompute.coordinator.repositories.task_repo import TaskRepository
from meshcompute.coordinator.repositories.worker_repo import WorkerRepository


class UnitOfWork:
    """Commit all repository changes together or roll them back on error."""

    def __enter__(self):
        self.session: Session = session_factory()()
        self._transaction = self.session.begin()
        self._transaction.__enter__()
        self.jobs = JobRepository(self.session)
        self.tasks = TaskRepository(self.session)
        self.workers = WorkerRepository(self.session)
        self.results = ResultRepository(self.session)
        self._committed = False
        self._events: list[dict] = []
        return self

    def commit(self) -> None:
        """Commit the current transaction explicitly before returning."""
        if not self._committed:
            self._transaction.commit()
            self._committed = True

    def collect_event(self, event: dict) -> None:
        """Collect an event for publication after commit (transactional outbox)."""
        self._events.append(event)

    def publish_collected(self) -> None:
        """Publish collected events after a successful commit."""
        from meshcompute.coordinator.events import event_hub

        for event in self._events:
            event_hub.publish(event)
        self._events.clear()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is not None:
                if not self._committed:
                    self._transaction.rollback()
            elif not self._committed:
                self._transaction.commit()
            return False
        finally:
            self.session.close()
