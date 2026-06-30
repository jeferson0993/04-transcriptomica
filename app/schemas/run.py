import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import PipelineStatus


class PipelineRunCreate(BaseModel):
    name: str
    samplesheet_path: str
    reference: str
    design_formula: str = "~condition"
    params: dict[str, object] | None = None


class PipelineRunResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: PipelineStatus
    samplesheet_path: str
    reference: str
    design_formula: str
    params: dict[str, object] | None
    nextflow_run_id: str | None
    output_dir: str | None
    report_path: str | None
    deseq2_report_path: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    error_message: str | None
    datalake_dataset_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PipelineRunList(BaseModel):
    items: list[PipelineRunResponse]
    total: int
