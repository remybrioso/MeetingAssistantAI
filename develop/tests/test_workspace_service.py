from pathlib import Path

from services.workspace_service import WorkspaceService


root_dir = Path("output") / "test_workspace"

service = WorkspaceService()

workspace = service.create(root_dir)

assert workspace.audio_dir.exists()
assert workspace.documents_dir.exists()
assert workspace.internal_dir.exists()

assert workspace.microphone_audio.name == "Microfono.wav"
assert workspace.system_audio.name == "Sistema.wav"
assert workspace.meeting_audio.name == "Reunion.wav"

assert workspace.summary_json.name == "summary.json"
assert workspace.summary_markdown.name == "Resumen.md"

print(workspace)

print()
print("WorkspaceService validado correctamente.")