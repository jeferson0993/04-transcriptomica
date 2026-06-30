import asyncio
import re

from app.config import settings


class MonitorService:
    def __init__(self) -> None:
        self.worker_container = settings.worker_container
        self.workspace = settings.workspace

    async def poll_logs(self, tail: int = 100) -> str:
        cmd = f"docker exec {self.worker_container} tail -n {tail} {self.workspace}/.nextflow.log"
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode() if stdout else ""

    async def check_status_from_logs(self) -> str | None:
        logs = await self.poll_logs(tail=50)
        if "Pipeline completed" in logs:
            return "completed"
        if "ERROR" in logs or "Error" in logs:
            return "failed"
        if "Submitted" in logs or "Running" in logs:
            return "running"
        return None

    async def get_error_message(self) -> str | None:
        logs = await self.poll_logs(tail=200)
        match = re.search(r"(?i)(error|exception|failed):?\s*(.+)$", logs, re.MULTILINE)
        if match:
            return match.group(0).strip()
        return None
