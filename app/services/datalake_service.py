import httpx

from app.config import settings


class DataLakeService:
    def __init__(self) -> None:
        self.api_url = settings.datalake_api_url

    async def register_dataset(
        self, name: str, source: str, layer: str,
        object_path: str, metadata: dict[str, object] | None = None,
    ) -> str | None:
        async with httpx.AsyncClient() as client:
            payload: dict[str, object] = {
                "name": name,
                "source": source,
                "layer": layer,
                "object_path": object_path,
                "metadata": metadata or {},
            }
            try:
                resp = await client.post(f"{self.api_url}/catalog", json=payload, timeout=10)
                resp.raise_for_status()
                data: dict[str, object] = resp.json()
                result = data.get("id")
                return str(result) if result is not None else None
            except Exception:
                return None
