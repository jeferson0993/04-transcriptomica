import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import references_router, runs_router
from app.config import settings
from app.database import async_session


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
    yield


app = FastAPI(title="Transcriptomics Pipeline API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{settings.domain}", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router, prefix="/runs", tags=["runs"])
app.include_router(references_router, prefix="/references", tags=["references"])


@app.get("/health")
async def health():
    db_ok = False
    minio_ok = False
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass
    try:
        from app.services.minio_service import MinioService
        ms = MinioService()
        minio_ok = ms.client.bucket_exists(settings.minio_bucket_processed)
    except Exception:
        pass
    status = "healthy" if (db_ok and minio_ok) else "degraded"
    return {"status": status, "database": db_ok, "minio": minio_ok}
