from services.meeting_pipeline_service import (
    MeetingPipelineService,
)


def test_meeting_pipeline_service_can_be_created() -> None:
    pipeline = MeetingPipelineService(
        summary_service=object(),
        validator=object(),
        storage_service=object(),
        markdown_exporter=object(),
    )

    assert pipeline is not None