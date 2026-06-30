from app.services.datalake_service import DataLakeService
from app.services.minio_service import MinioService
from app.services.monitor_service import MonitorService
from app.services.pipeline_service import PipelineService


def test_pipeline_service_init():
    svc = PipelineService()
    assert svc.max_concurrent >= 1
    assert svc.default_profile == "docker,eco"


def test_minio_service_init():
    svc = MinioService()
    assert svc.client is not None


def test_datalake_service_init():
    svc = DataLakeService()
    assert svc.api_url is not None


def test_monitor_service_init():
    svc = MonitorService()
    assert svc.worker_container is not None
