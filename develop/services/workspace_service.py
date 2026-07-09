"""
workspace_service.py

Crea la estructura física de una reunión.
"""

from models.workspace.meeting_workspace import MeetingWorkspace


class WorkspaceService:

    def create(
        self,
        root_dir
    ) -> MeetingWorkspace:

        audio_dir = root_dir / "Audio"
        documents_dir = root_dir / "Documentos"
        internal_dir = root_dir / ".mai"

        audio_dir.mkdir(parents=True, exist_ok=True)
        documents_dir.mkdir(parents=True, exist_ok=True)
        internal_dir.mkdir(parents=True, exist_ok=True)

        return MeetingWorkspace(
            root_dir=root_dir,
            audio_dir=audio_dir,
            documents_dir=documents_dir,
            internal_dir=internal_dir
        )