import asyncio
import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.enums import PipelineStatus
from app.models.run import PipelineRun


class PipelineService:
    def __init__(self) -> None:
        self.worker_container = settings.worker_container
        self.pipeline_dir = settings.pipeline_dir
        self.workspace = settings.workspace
        self.max_concurrent = settings.max_concurrent_runs
        self.default_profile = settings.default_profile

    async def _count_active_runs(self, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count(PipelineRun.id)).where(
                PipelineRun.status.in_([PipelineStatus.queued, PipelineStatus.running])
            )
        )
        return result.scalar() or 0

    async def dispatch(self, run: PipelineRun) -> str:
        params = run.params or {}
        params_json = json.dumps(params)
        cmd = (
            f"docker exec {self.worker_container} nextflow run {self.pipeline_dir}/main.nf "
            f"-profile {self.default_profile} "
            f"--samplesheet {run.samplesheet_path} "
            f"--reference {run.reference} "
            f"--design_formula '{run.design_formula}' "
            f"--outdir {self.workspace}/results/{run.id} "
            f"--run_id {run.id} "
            f"-params-file <(echo '{params_json}') "
            f"> {self.workspace}/logs/{run.id}.log 2>&1"
        )
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        run.nextflow_run_id = str(proc.pid)
        return str(proc.pid)

    async def cancel(self, run: PipelineRun) -> None:
        if run.nextflow_run_id:
            cmd = f"docker exec {self.worker_container} nextflow cancel {run.nextflow_run_id}"
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
