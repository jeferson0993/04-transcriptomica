import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.enums import PipelineStatus
from app.models.run import PipelineRun
from app.schemas.run import PipelineRunCreate, PipelineRunList, PipelineRunResponse
from app.services.monitor_service import MonitorService
from app.services.pipeline_service import PipelineService
from app.services.report_service import ReportService

router = APIRouter()


@router.post("", response_model=PipelineRunResponse, status_code=201)
async def create_run(body: PipelineRunCreate, session: AsyncSession = Depends(get_session)):
    pipeline_service = PipelineService()
    active = await pipeline_service._count_active_runs(session)
    if active >= pipeline_service.max_concurrent:
        msg = f"Maximum concurrent runs ({pipeline_service.max_concurrent}) reached"
        raise HTTPException(status_code=429, detail=msg)

    run = PipelineRun(
        name=body.name,
        samplesheet_path=body.samplesheet_path,
        reference=body.reference,
        design_formula=body.design_formula,
        params=body.params or {},
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    await pipeline_service.dispatch(run)
    return run


@router.get("", response_model=PipelineRunList)
async def list_runs(
    status: PipelineStatus | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    query = select(PipelineRun)
    count_query = select(func.count(PipelineRun.id))
    if status:
        query = query.where(PipelineRun.status == status)
        count_query = count_query.where(PipelineRun.status == status)
    query = query.order_by(PipelineRun.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    total_result = await session.execute(count_query)
    runs = list(result.scalars().all())
    total = total_result.scalar() or 0
    items = [PipelineRunResponse.model_validate(r) for r in runs]
    return PipelineRunList(items=items, total=total)


@router.get("/{run_id}", response_model=PipelineRunResponse)
async def get_run(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/logs")
async def get_run_logs(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    monitor = MonitorService()
    logs = await monitor.poll_logs()
    return {"logs": logs}


@router.get("/{run_id}/report")
async def get_run_report(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if not run.report_path:
        raise HTTPException(status_code=404, detail="Report not available yet")
    return {"report_path": run.report_path}


@router.get("/{run_id}/deseq2-report")
async def get_deseq2_report(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if not run.deseq2_report_path:
        raise HTTPException(status_code=404, detail="DESeq2 report not available yet")
    return {"report_path": run.deseq2_report_path}


@router.get("/{run_id}/results/{file_path:path}")
async def download_result(
    run_id: uuid.UUID,
    file_path: str,
    session: AsyncSession = Depends(get_session),
):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    from app.services.minio_service import MinioService
    ms = MinioService()
    object_name = f"runs/{run_id}/{file_path}"
    if not ms.object_exists(settings.minio_bucket_processed, object_name):
        raise HTTPException(status_code=404, detail="File not found")
    data = ms.download_bytes(settings.minio_bucket_processed, object_name)
    from fastapi.responses import Response
    return Response(content=data, media_type="application/octet-stream")


@router.get("/{run_id}/r-report", response_class=HTMLResponse)
async def get_run_r_report(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> str:
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    svc = ReportService()
    html = await svc.read_deseq2_report(str(run_id))
    if html is None:
        raise HTTPException(status_code=404, detail="DESeq2 report not available yet")
    return html


@router.post("/{run_id}/cancel", response_model=PipelineRunResponse)
async def cancel_run(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    run = await session.get(PipelineRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.status in (PipelineStatus.completed, PipelineStatus.failed, PipelineStatus.cancelled):
        raise HTTPException(status_code=400, detail=f"Run already in state: {run.status}")
    pipeline_service = PipelineService()
    await pipeline_service.cancel(run)
    run.status = PipelineStatus.cancelled
    await session.commit()
    return run
