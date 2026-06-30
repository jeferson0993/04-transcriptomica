import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.reference import TranscriptomeRef
from app.schemas.reference import ReferenceCreate, ReferenceResponse

router = APIRouter()


@router.post("", response_model=ReferenceResponse, status_code=201)
async def create_reference(body: ReferenceCreate, session: AsyncSession = Depends(get_session)):
    stmt = select(TranscriptomeRef).where(TranscriptomeRef.name == body.name)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Reference with this name already exists")
    ref = TranscriptomeRef(**body.model_dump())
    session.add(ref)
    await session.commit()
    await session.refresh(ref)
    return ref


@router.get("", response_model=list[ReferenceResponse])
async def list_references(session: AsyncSession = Depends(get_session)):
    stmt = select(TranscriptomeRef).order_by(TranscriptomeRef.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{ref_id}", response_model=ReferenceResponse)
async def get_reference(ref_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    ref = await session.get(TranscriptomeRef, ref_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    return ref
