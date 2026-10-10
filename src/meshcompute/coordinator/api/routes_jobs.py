"""Job submission and read-only job endpoints."""
from uuid import UUID
from fastapi import APIRouter,Depends,Query,status
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.api.schemas import JobAccepted,JobPage,JobSubmission,JobView,TaskPageItem
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.job_service import JobService

router=APIRouter(prefix="/jobs",tags=["jobs"])
service=JobService()
@router.post("",response_model=JobAccepted,status_code=status.HTTP_202_ACCEPTED)
async def submit_job(request: JobSubmission,uow: UnitOfWork=Depends(get_uow)):
    """Accept a registered job and return its identifier immediately."""
    return await service.submit(uow,request)
@router.get("",response_model=JobPage)
def list_jobs(limit: int=Query(default=50,ge=1,le=200),offset: int=Query(default=0,ge=0),uow: UnitOfWork=Depends(get_uow)):
    """List recent jobs with task-state counts."""
    return service.list(uow,limit,offset)
@router.get("/{job_id}/tasks",response_model=list[TaskPageItem])
def get_job_tasks(job_id: UUID,uow: UnitOfWork=Depends(get_uow)):
    """Show per-task attempt and lease state."""
    return service.tasks(uow,job_id)
@router.get("/{job_id}",response_model=JobView)
def get_job(job_id: UUID,uow: UnitOfWork=Depends(get_uow)):
    """Return progress counts for a submitted job."""
    return service.get(uow,job_id)
@router.get("/{job_id}/result")
def get_job_result(job_id: UUID,uow: UnitOfWork=Depends(get_uow)):
    """Return the merged result only after every task succeeds."""
    return service.result(uow,job_id)
