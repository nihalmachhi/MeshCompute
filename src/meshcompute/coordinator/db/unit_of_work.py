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
        self.session: Session=session_factory()()
        self._transaction=self.session.begin()
        self._transaction.__enter__()
        self.jobs=JobRepository(self.session)
        self.tasks=TaskRepository(self.session)
        self.workers=WorkerRepository(self.session)
        self.results=ResultRepository(self.session)
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        try: return self._transaction.__exit__(exc_type,exc_value,traceback)
        finally: self.session.close()
