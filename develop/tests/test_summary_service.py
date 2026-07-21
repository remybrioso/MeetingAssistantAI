from pathlib import Path
import json

from services.summary_service import SummaryService


meeting_dirs = sorted(
    Path("output").glob("meeting_*"),
    reverse=True
)

if not meeting_dirs:
    raise FileNotFoundError(
        "No hay reuniones en output/meeting_*"
    )

latest = meeting_dirs[0]

transcript_file = latest / ".mai" / "transcript.json"

if not transcript_file.exists():
    raise FileNotFoundError(
        f"No existe {transcript_file}"
    )

service = SummaryService()

summary = service.generate_from_transcript(
    transcript_file
)

summary_file = latest / "summary.json"

with open(summary_file, "w", encoding="utf-8") as file:
    json.dump(
        summary.as_dict(),
        file,
        ensure_ascii=False,
        indent=4
    )

print(summary.as_dict())

assert summary.title
assert summary.executive_summary
assert len(summary.key_points) > 0

print()
print("summary.json generado correctamente.")