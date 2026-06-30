"""Create initial tables for transcriptomics pipeline

Revision ID: 0001
Revises:
Create Date: 2026-06-12

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("pending", "queued", "running", "completed", "failed", "cancelled", name="pipelinestatus"), nullable=False),
        sa.Column("samplesheet_path", sa.String(500), nullable=False),
        sa.Column("reference", sa.String(255), nullable=False),
        sa.Column("design_formula", sa.String(255), nullable=False, server_default="~condition"),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("nextflow_run_id", sa.String(100), nullable=True),
        sa.Column("output_dir", sa.String(500), nullable=True),
        sa.Column("report_path", sa.String(500), nullable=True),
        sa.Column("deseq2_report_path", sa.String(500), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("datalake_dataset_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transcriptome_refs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("species", sa.String(255), nullable=False, server_default="Homo sapiens"),
        sa.Column("fasta_path", sa.String(500), nullable=False),
        sa.Column("gtf_path", sa.String(500), nullable=False),
        sa.Column("star_index_path", sa.String(500), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("transcriptome_refs")
    op.drop_table("pipeline_runs")
    op.execute("DROP TYPE IF EXISTS pipelinestatus")
