from app.models.enums import PipelineStatus


def test_pipeline_status_values():
    assert PipelineStatus.pending == "pending"
    assert PipelineStatus.queued == "queued"
    assert PipelineStatus.running == "running"
    assert PipelineStatus.completed == "completed"
    assert PipelineStatus.failed == "failed"
    assert PipelineStatus.cancelled == "cancelled"


def test_pipeline_status_all():
    assert len(PipelineStatus) == 6
