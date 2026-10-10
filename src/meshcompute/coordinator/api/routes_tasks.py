"""Worker task claim, start, completion, and retry endpoints."""
from uuid import UUID
from fastapi import APIRouter,Depends,Response,status
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.api.schemas import ClaimedTask,TaskClaimRequest,TaskCompleteRequest,TaskFailureRequest,TaskMutationResponse,TaskStartRequest
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.scheduler import SchedulerService
from meshcompute.coordinator.services.task_service import TaskService

router=APIRouter(prefix="/tasks",tags=["tasks"])
scheduler=SchedulerService()
tasks=TaskService()
@router.post("/claim",response_model=ClaimedTask|None)
async def claim_task(request: TaskClaimRequest,response: Response,uow: UnitOfWork=Depends(get_uow)):
    """Lease the oldest pending task to one idle worker."""
    task=await scheduler.claim(uow,request.worker_id)
    if task is None:response.status_code=status.HTTP_204_NO_CONTENT;return None
    return task
@router.post("/{task_id}/start")
async def start_task(task_id: UUID,request: TaskStartRequest,uow: UnitOfWork=Depends(get_uow)):
    """Record the transition from ASSIGNED to RUNNING."""
    return await scheduler.start(uow,task_id,request.worker_id,request.attempt)
@router.post("/{task_id}/complete",response_model=TaskMutationResponse)
async def complete_task(task_id: UUID,request: TaskCompleteRequest,uow: UnitOfWork=Depends(get_uow)):
    """Commit a fenced task result and trigger job aggregation."""
    return await tasks.complete(uow,task_id,request.worker_id,request.attempt,request.output,request.duration_ms)
@router.post("/{task_id}/fail",response_model=TaskMutationResponse)
async def fail_task(task_id: UUID,request: TaskFailureRequest,uow: UnitOfWork=Depends(get_uow)):
    """Retry the attempt or fail the task when its budget is exhausted."""
    return await tasks.fail(uow,task_id,request.worker_id,request.attempt,request.error)
