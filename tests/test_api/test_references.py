import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_create_reference(client: httpx.AsyncClient):
    resp = await client.post("/references", json={
        "name": "grch38_gencode_v44",
        "species": "Homo sapiens",
        "fasta_path": "/ref/grch38/genome.fa",
        "gtf_path": "/ref/grch38/gencode.v44.annotation.gtf",
        "star_index_path": "/ref/grch38/star_index",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "grch38_gencode_v44"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_reference(client: httpx.AsyncClient):
    resp = await client.post("/references", json={
        "name": "grch38_gencode_v44",
        "fasta_path": "/ref/test.fa",
        "gtf_path": "/ref/test.gtf",
        "star_index_path": "/ref/star",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_references(client: httpx.AsyncClient):
    resp = await client.get("/references")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_reference(client: httpx.AsyncClient):
    create_resp = await client.post("/references", json={
        "name": "test_ref_list",
        "fasta_path": "/ref/test.fa",
        "gtf_path": "/ref/test.gtf",
        "star_index_path": "/ref/star",
    })
    ref_id = create_resp.json()["id"]

    resp = await client.get(f"/references/{ref_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "test_ref_list"


@pytest.mark.asyncio
async def test_get_reference_not_found(client: httpx.AsyncClient):
    resp = await client.get(f"/references/{uuid.uuid4()}")
    assert resp.status_code == 404
