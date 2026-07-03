from models.recording_session import RecordingSession


session = RecordingSession()

print()
print("Session:", session.session_name)
print("Dir:", session.session_dir)
print("Mic:", session.mic_file)
print("System:", session.system_file)
print("Meeting:", session.meeting_file)
print("Metadata:", session.metadata_file)

assert session.session_dir.exists()
assert session.mic_file.name == "mic.wav"
assert session.system_file.name == "system.wav"
assert session.meeting_file.name == "meeting.wav"
assert session.metadata_file.name == "metadata.json"

print()
print("Prueba satisfactoria.")