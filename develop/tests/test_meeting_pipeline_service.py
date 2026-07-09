from services.meeting_pipeline_service import (
    MeetingPipelineService
)

pipeline = MeetingPipelineService(
    summary_service=object(),
    validator=object(),
    storage_service=object(),
    markdown_exporter=object()
)

print(pipeline)

assert pipeline is not None

print()
print("MeetingPipelineService creado correctamente.")