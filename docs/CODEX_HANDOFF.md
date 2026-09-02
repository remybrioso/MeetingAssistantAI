# CODEX_HANDOFF — Meeting Assistant AI

## 1. Purpose
This document transfers the engineering state of Meeting Assistant AI (MAI) into Codex.

Codex must read this document and the repository before changing code.

## 2. Repository state at handoff
Repository: `remybrioso/MeetingAssistantAI`

Corporate checkout:
`C:\Proyectos\MeetingAssistantAI`

Development directory:
`C:\Proyectos\MeetingAssistantAI\develop`

Current branch:
`task-065-corporate-acceptance-hardening`

Release baseline:
`c67e32965febfc3e5a9f2dafcb9cbd7a159bf622`
`chore: prepare v0.9.0-alpha.2 release`

Current Corporate Acceptance commits:
- `7af7eba` — `fix: harden Ollama structured output contracts`
- `d1ce1db` — `fix: harden temporal transcript integrity`

Expected unrelated working-tree files:
- modified: `Meeting Assistan AI_workflow.txt`
- untracked: `docs/Meeting_Assistant_AI_workflow_actualizado.txt`

Do not stage, modify, delete, rename, or clean those files.

## 3. Current release
Published internal/private prerelease:
`v0.9.0-alpha.2`

Release commit:
`c67e32965febfc3e5a9f2dafcb9cbd7a159bf622`

Windows installer:
`MeetingAssistantAI-Setup-v0.9.0-alpha.2.exe`

Known SHA256:
`D2849EDBF498D5B3803C04E307CDF7735780D54A9DF74B12E350D425364615D6`

Do not overwrite or retag alpha.2. Acceptance fixes should lead to a new release, likely `v0.9.0-alpha.3`.

## 4. Product architecture
Primary production flow:

GUI / Import
→ RecordingSession + MeetingWorkspace
→ TranscriptService
→ Faster-Whisper
→ Transcript
→ TranscriptChunker
→ staged per-chunk Meeting Intelligence
→ MeetingKnowledge
→ staged global consolidation
→ MeetingReport
→ deterministic Artifact Delivery

Primary artifacts:
- `.mai/meeting_report.json`
- `.mai/action_items.json`
- `.mai/decisions.json`
- `.mai/transcript.json`
- `.mai/processing_metrics.json`
- `.mai/workspace.json`
- `Documentos/Meeting Report.md`
- `Documentos/minutes.docx`
- `Documentos/meeting.pdf`

Recorded meetings use separate source tracks:
- `Audio/Microfono.wav` → LOCAL
- `Audio/Sistema.wav` → REMOTE

Runtime:
- Windows
- Python 3.14 development environment
- PyInstaller one-folder frozen runtime
- Inno Setup installer
- Faster-Whisper local transcription
- Ollama external local AI provider
- production model `qwen2.5:3b`

## 5. Completed major tasks
- TASK-057 — staged meeting intelligence and global consolidation: closed.
- TASK-058 — deterministic artifact delivery: closed.
- TASK-059 — release alignment: closed.
- TASK-060 — packaging-ready runtime: closed.
- TASK-061 — Windows executable: closed.
- TASK-062 — Windows installer: closed.
- TASK-063 — first-run onboarding: closed.
- TASK-064 — private prerelease `v0.9.0-alpha.2`: closed.

## 6. TASK-065 — Corporate Acceptance
Ongoing on a real TSS Windows workstation.

Corporate workstation facts:
- Intel i7-12700K
- ~16 GB RAM
- local Ollama
- Faster-Whisper
- corporate OneDrive-backed Documents path
- PowerShell execution policy blocks normal `.venv` activation
- use `\.venv\Scripts\python.exe ...` directly
- do not change execution policy

## 7. CAT-001 — insufficient meeting evidence UX
Status: open, lower priority.

A non-meeting Spanish news/narrative recording captured and transcribed correctly but produced:
`MeetingKnowledge no contiene conocimiento suficiente para generar un MeetingReport`

Desired future UX should clearly say that the transcript was saved but insufficient meeting content was found.

Do not mix this into unrelated tasks.

## 8. CAT-002 — imported session runtime path
Status: open.

`RecordingSession` defaults to `base_output_dir: str = "output"`.

`ImportedMeetingService` creates an imported session without supplying the canonical Meetings directory.

In the installed runtime this can place imported user data under the installed application tree:
`%LOCALAPPDATA%\Programs\Meeting Assistant AI\output\...`

This violates the runtime path contract and risks user data living in an uninstall-controlled directory.

Fix separately after the higher-priority intelligence failures.

## 9. CAT-003 / TASK-065A — Ollama structured-output grammar
Status: CLOSED.

Commit:
`7af7eba`
`fix: harden Ollama structured output contracts`

Original failure:
Ollama/llama.cpp rejected a productive JSON schema due to an excessive repetition bound and returned HTTP 400.

065A changed exactly:
- `develop/prompts/schemas/meeting_report_narrative_v1.json`
- `develop/prompts/schemas/meeting_semantic_consolidation_v1.json`
- `develop/providers/ollama_provider.py`
- `develop/tests/integration/ai/test_real_structured_output_contracts.py`
- `develop/tests/unit/ai/test_ollama_provider_generate.py`
- `develop/tests/unit/ai/test_productive_json_schema_compatibility.py`

Evidence:
- targeted unit tests passed
- real Ollama productive-schema integration passed
- source application import E2E passed
- all expected artifacts generated
- scoped regression: `949 passed, 2 skipped, 2 deselected`

Do not reopen 065A without new evidence.

## 10. CAT-004 / TASK-065B — temporal transcript integrity
Status: CLOSED.

Commit:
`d1ce1db`
`fix: harden temporal transcript integrity`

Original real-meeting error:
`ChunkKnowledge decisions elemento #1 evidence elemento #73 está fuera del rango temporal del chunk.`

A LOCAL Faster-Whisper segment contained a catastrophic discontinuity:
- segment start ~736.3
- early words ended ~741.94
- next words began ~2052.42
- segment end ~2061.52
- internal gap ~1310.48 seconds (~21m 50.48s)

The old `TranscriptChunk` range used the first segment start and last segment end, which assumes monotonic end times after sorting by start. That is false for overlapping LOCAL/REMOTE tracks.

065B changed/added:
- `develop/models/transcript_chunk.py`
- `develop/providers/whisper/whisper_provider.py`
- `develop/providers/whisper/whisper_segment_normalizer.py`
- `develop/tests/unit/transcription/test_transcript_chunker.py`
- `develop/tests/unit/transcription/test_whisper_provider_segment_normalization.py`
- `develop/tests/unit/transcription/test_whisper_segment_normalizer.py`

Behavior:
1. Normalize Faster-Whisper segments using word timestamps.
2. Split when the gap between consecutive words is greater than 10 seconds.
3. Preserve normal contiguous segments unchanged.
4. `TranscriptChunk.start = min(segment.start)`.
5. `TranscriptChunk.end = max(segment.end)`.

Evidence:
- targeted tests: `20 passed`
- transcription unit regression: `47 passed`

Real meeting after recovery:
- segments: 304
- words: 4027
- chunks: 4
- maximum internal word gap: 5.890 s
- gaps >10 s: 0
- chunk range violations: 0

Chunk ranges:
- chunk 0: 86 segments, 1189 words, 1.34 → 757.23
- chunk 1: 75 segments, 1198 words, 757.39 → 1297.15
- chunk 2: 105 segments, 1197 words, 1297.15 → 1879.19
- chunk 3: 38 segments, 440 words, 1879.19 → 2061.52

The original CAT-004 error did not recur.

## 11. Real acceptance fixture
Do not delete:
`meeting_20260901_140443`

Expected path:
`C:\Users\remi_brioso\OneDrive - TESORERIA DE LA SEGURIDAD SOCIAL (TSS)\Documents\Meeting Assistant AI\Meetings\meeting_20260901_140443`

The original audio survived:
- `Microfono.wav` ~2118.163 s, 44.1 kHz, mono
- `Sistema.wav` 2118 s, 44.1 kHz, stereo, PCM16

This meeting remains the primary Corporate Acceptance E2E fixture until full report delivery succeeds.

## 12. CAT-005 — global exact-coverage fragility
Status: ROOT CAUSE CONFIRMED.
Fix not yet implemented.

After 065B, the real meeting progressed further and failed during G1 semantic consolidation:

`La consolidación semántica omitió items fuente obligatorios: ('risk', 3, 0).`

The corrected transcript produces four chunks.

Real MeetingKnowledge:
Chunk 0:
- topics=1
- decisions=1
- actions=0
- risks=1
- pending=0

Chunk 1:
- topics=0
- decisions=1
- actions=0
- risks=0
- pending=0

Chunk 2:
- topics=0
- decisions=1
- actions=0
- risks=1
- pending=0

Chunk 3:
- topics=0
- decisions=0
- actions=0
- risks=1
- pending=0

Global totals:
- topics=1
- decisions=3
- actions=0
- risks=3
- pending=0
- TOTAL=7

G1 catalog:
- 7 entries
- 1052 characters
- 1057 UTF-8 bytes

References by chunk:
- chunk 0: 3
- chunk 1: 1
- chunk 2: 2
- chunk 3: 1

Root-cause conclusion:
CAT-005 is not a large-catalog problem.

The model omitted one source item despite receiving only seven items and roughly 1 KB of catalog data.

Current G1 asks the LLM to do both semantic consolidation and exact source-reference bookkeeping. The parser then rejects the whole meeting if one expected reference is missing.

There is a parallel fragility in G2: `executive_summary.source_item_ids` is also required to contain all semantic item IDs exactly once.

## 13. TASK-065C — Deterministic Global Coverage
Status: NEXT IMPLEMENTATION TASK.

Core principle:

`LLM = semantic intelligence`
`Code = integrity, coverage, provenance`

Do not solve CAT-005 by:
- increasing retries;
- weakening validation and silently accepting lost knowledge;
- changing qwen2.5:3b just to mask the issue;
- removing grounding;
- relying on the model for exact bookkeeping.

### Intended G1 behavior
The LLM still decides semantic merging and consolidated wording.

Continue rejecting:
- invalid JSON
- wrong fields
- invalid kinds
- nonexistent references
- wrong-kind references
- duplicate references
- reuse of one source reference across multiple consolidated items

But missing source references should be reconciled deterministically after parsing.

For each expected MeetingKnowledge source item absent from the otherwise-valid G1 response:
- preserve original kind
- preserve/derive original source description
- create a standalone consolidated item
- assign original `chunk_index` and `item_index`

Then assert exact 100% source coverage in code.

Real failure example:
if G1 misses `('risk', 3, 0)`, append a standalone risk backed by `chunk_index=3`, `item_index=0`.

No information loss. No extra LLM call.

### Intended G2 behavior
G2 continues to generate:
- title
- optional objective
- executive-summary text
- key points

Continue rejecting invalid/nonexistent/duplicate IDs.

For executive-summary provenance, code should own full coverage.

After valid narrative parsing, final executive-summary IDs should deterministically cover:
`list(range(len(semantic_consolidation.items)))`

Keep the model's executive-summary text unchanged.

Title, objective, and key-point references should remain genuinely model-grounded and keep existing validation.

### Proposed scope
Inspect current source/tests before editing and confirm the smallest clean scope.

Expected production changes:
- modify `develop/services/meeting_semantic_consolidation_parser.py`
- add `develop/services/meeting_semantic_coverage_service.py`
- modify `develop/services/meeting_report_narrative_parser.py`
- add `develop/services/meeting_report_narrative_coverage_service.py`
- modify `develop/services/staged_meeting_report_consolidation_service.py`

Expected tests:
- semantic coverage reconciliation unit tests
- narrative coverage reconciliation unit tests
- parser tests preserving strictness for malformed/invalid references
- staged consolidation service tests
- regression for seven source items with one omitted risk

Do not modify 065A schemas or `OllamaProvider` unless new evidence proves it necessary.
Do not modify 065B files as part of 065C.

### Required 065C gates
1. Inspect relevant source/tests.
2. State exact implementation scope before edits.
3. Implement G1 deterministic coverage.
4. Targeted G1 tests.
5. Implement G2 deterministic provenance.
6. Targeted G2 tests.
7. Staged consolidation regression.
8. Source-level E2E using the corrected real meeting transcript.
9. Verify all expected report artifacts.
10. Run appropriate broader regression.
11. Inspect staged Git diff explicitly.
12. Commit only the 065C scope.

Do not retranscribe the 35-minute audio unless a test specifically requires revalidation of 065B. Reuse the corrected `.mai/transcript.json`.

## 14. Expected E2E after 065C
Corrected transcript
→ four chunks
→ per-chunk knowledge
→ deterministic G1 coverage
→ G2 narrative
→ deterministic executive-summary provenance
→ MeetingReport
→ Artifact Delivery

Expected final artifacts:
- `.mai/meeting_report.json`
- `.mai/action_items.json`
- `.mai/decisions.json`
- `Documentos/Meeting Report.md`
- `Documentos/minutes.docx`
- `Documentos/meeting.pdf`

The omitted risk must remain represented.

## 15. Remaining acceptance work after 065C
1. CAT-002 — imported session canonical runtime path.
2. CAT-001 — insufficient-meeting-evidence UX.
3. broader regression.
4. installed/frozen acceptance as needed.
5. dependency recovery checks.
6. uninstall / user-data preservation / reinstall.
7. new Windows build and installer.
8. new prerelease, likely `v0.9.0-alpha.3`.

## 16. First Codex instruction
Read `AGENTS.md` and `docs/CODEX_HANDOFF.md` completely, then inspect the repository and current Git state.

Do not modify anything yet.

Confirm:
1. current branch and release baseline;
2. TASK-065A state;
3. TASK-065B state;
4. CAT-005 root cause;
5. proposed TASK-065C architecture;
6. files that must never be touched;
7. test and commit rules.

Then inspect the relevant G1/G2 implementation and tests and propose the exact minimal file scope for TASK-065C before making changes.
