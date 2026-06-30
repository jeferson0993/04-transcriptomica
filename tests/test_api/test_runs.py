import uuid
from unittest.mock import patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PipelineStatus
from app.models.run import PipelineRun


@pytest.mark.asyncio
async def test_create_run(client: httpx.AsyncClient, session: AsyncSession):
    count_active = "app.services.pipeline_service.PipelineService._count_active_runs"
    with patch(count_active, return_value=0), \
         patch("app.services.pipeline_service.PipelineService.dispatch"):
        resp = await client.post("/runs", json={
            "name": "test_run",
            "samplesheet_path": "minio://samplesheets/test.csv",
            "reference": "grch38_gencode_v44",
            "design_formula": "~condition",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test_run"
    assert data["status"] == "pending"
    assert data["reference"] == "grch38_gencode_v44"
    assert data["design_formula"] == "~condition"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_runs(client: httpx.AsyncClient, session: AsyncSession):
    resp = await client.get("/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_runs_with_filter(client: httpx.AsyncClient, session: AsyncSession):
    run = PipelineRun(
        name="completed_run",
        samplesheet_path="minio://test.csv",
        reference="grch38",
        status=PipelineStatus.completed,
    )
    session.add(run)
    await session.commit()

    resp = await client.get("/runs?status=completed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(r["status"] == "completed" for r in data["items"])


@pytest.mark.asyncio
async def test_get_run_not_found(client: httpx.AsyncClient):
    resp = await client.get(f"/runs/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_nonexistent_run(client: httpx.AsyncClient):
    resp = await client.post(f"/runs/{uuid.uuid4()}/cancel")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_run_logs(client: httpx.AsyncClient, session: AsyncSession):
    run = PipelineRun(
        name="logs_test",
        samplesheet_path="minio://test.csv",
        reference="grch38",
    )
    session.add(run)
    await session.commit()

    resp = await client.get(f"/runs/{run.id}/logs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_run_report_not_found(client: httpx.AsyncClient, session: AsyncSession):
    run = PipelineRun(
        name="report_test",
        samplesheet_path="minio://test.csv",
        reference="grch38",
    )
    session.add(run)
    await session.commit()

    resp = await client.get(f"/runs/{run.id}/report")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_run_deseq2_report_not_found(client: httpx.AsyncClient, session: AsyncSession):
    run = PipelineRun(
        name="deseq2_test",
        samplesheet_path="minio://test.csv",
        reference="grch38",
    )
    session.add(run)
    await session.commit()

    resp = await client.get(f"/runs/{run.id}/deseq2-report")
    assert resp.status_code == 404
