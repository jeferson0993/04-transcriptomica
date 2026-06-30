import uuid
from datetime import datetime

from pydantic import BaseModel


class ReferenceCreate(BaseModel):
    name: str
    species: str = "Homo sapiens"
    fasta_path: str
    gtf_path: str
    star_index_path: str
    is_default: bool = False


class ReferenceResponse(BaseModel):
    id: uuid.UUID
    name: str
    species: str
    fasta_path: str
    gtf_path: str
    star_index_path: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
