from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.api.deps import get_current_user
from app.schemas.apply import ApplyRequest, ApplyResponse
from app.services.apply_service import queue_auto_apply, process_auto_apply_batch

router = APIRouter()


@router.post("/", response_model=ApplyResponse)
async def auto_apply(
    payload: ApplyRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    if not payload.job_ids:
        raise HTTPException(status_code=400, detail="job_ids cannot be empty")

    queued, already, failed = queue_auto_apply(
        user=current_user,
        job_ids=payload.job_ids,
        override_email=payload.override_email,
    )

    # Trigger async processing of queue in background
    background_tasks.add_task(process_auto_apply_batch, limit=10)

    return ApplyResponse(
        queued=queued,
        already_queued=already,
        failed=failed,
    )
