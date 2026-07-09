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

        workspace = MeetingWorkspace(
            root_dir=root_dir,
            audio_dir=root_dir / "Audio",
            documents_dir=root_dir / "Documentos",
            internal_dir=root_dir / ".mai"
        )
        workspace.initialize()

        return workspace
