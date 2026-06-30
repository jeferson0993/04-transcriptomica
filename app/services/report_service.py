import asyncio

from app.config import settings


class ReportService:
    def __init__(self) -> None:
        self.worker_container = settings.worker_container
        self.workspace = settings.workspace

    async def read_deseq2_report(self, run_id: str) -> str | None:
        report_path = f"{self.workspace}/results_{run_id}/deseq2_report.html"
        cmd = f"docker exec {self.worker_container} cat {report_path}"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0 and stdout:
            return stdout.decode()
        return None
