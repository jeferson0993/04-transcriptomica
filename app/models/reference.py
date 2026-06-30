import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TranscriptomeRef(Base):
    __tablename__ = "transcriptome_refs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    species: Mapped[str] = mapped_column(String(255), nullable=False, default="Homo sapiens")
    fasta_path: Mapped[str] = mapped_column(String(500), nullable=False)
    gtf_path: Mapped[str] = mapped_column(String(500), nullable=False)
    star_index_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
