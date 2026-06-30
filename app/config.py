from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/transcriptomics"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_raw: str = "raw"
    minio_bucket_processed: str = "processed"
    minio_bucket_curated: str = "curated"
    minio_secure: bool = False

    ref_dir: str = "/ref"
    workspace: str = "/workspace"
    pipeline_dir: str = "/pipeline"
    worker_container: str = "transcriptomics-worker"
    default_profile: str = "docker,eco"
    max_concurrent_runs: int = 2

    datalake_api_url: str = "http://api-data-lake:8000"
    domain: str = "localhost"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
