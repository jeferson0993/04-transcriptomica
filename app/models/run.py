import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import PipelineStatus


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PipelineStatus] = mapped_column(
        Enum(PipelineStatus), default=PipelineStatus.pending, nullable=False
    )
    samplesheet_path: Mapped[str] = mapped_column(String(500), nullable=False)
    reference: Mapped[str] = mapped_column(String(255), nullable=False)
    design_formula: Mapped[str] = mapped_column(String(255), nullable=False, default="~condition")
    params: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    nextflow_run_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    output_dir: Mapped[str | None] = mapped_column(String(500), nullable=True)
    report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deseq2_report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    datalake_dataset_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
