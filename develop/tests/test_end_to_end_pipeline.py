from pathlib import Path

meeting_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

assert meeting_dirs

latest = meeting_dirs[0]

assert (latest / "transcript.json").exists()

print()
print("Pipeline End-to-End correcto.")