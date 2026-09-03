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

Validated HEAD:
`3209fe666b6ce0ae9659494a6ec5a95ae994d83d`

Release baseline:
`c67e32965febfc3e5a9f2dafcb9cbd7a159bf622`
`chore: prepare v0.9.0-alpha.2 release`

Corporate Acceptance commits:
- `7af7eba` — `fix: harden Ollama structured output contracts`
- `d1ce1db` — `fix: harden temporal transcript integrity`
- `0f17f27` — `docs: add Codex engineering handoff`
- `1676a79` — `fix: harden global meeting report integrity`
- `f970d38` — `fix: use canonical path for imported meetings`
- `b8eeac2` — `test: avoid imported meeting module collision`
- `3209fe6` — `fix: handle insufficient meeting evidence gracefully`

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

Do not overwrite or retag alpha.2.

Next intended prerelease:
`v0.9.0-alpha.3`

TASK-065 production work is complete at the validated HEAD. No production change remains required before release metadata preparation.

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
Status: CLOSED.

- TASK-065A — Ollama structured-output compatibility: CLOSED.
- TASK-065B — temporal transcript integrity: CLOSED.
- TASK-065C — global semantic/narrative integrity: CLOSED.
- TASK-065D — broad regression: CLOSED.
- TASK-065E — imported canonical runtime path: CLOSED.
- TASK-065F — insufficient-evidence UX: CLOSED.

Resolved acceptance findings:
- CAT-001 — insufficient-evidence UX: RESOLVED.
- CAT-002 — imported meeting path: RESOLVED.
- CAT-003 — Ollama structured-output grammar: RESOLVED.
- CAT-004 — temporal integrity: RESOLVED.
- CAT-005 — semantic/narrative integrity: RESOLVED.

Final regression:
- 1018 collected
- 1016 passed
- 2 skipped
- 0 failed

Frozen acceptance:
- CAT-001: PASS
- CAT-002: PASS

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
Status: RESOLVED by TASK-065F.

Commit:
`3209fe6`
`fix: handle insufficient meeting evidence gracefully`

Expected structural and semantic insufficiency now propagate through typed domain exceptions as an expected outcome, not as a technical processing failure.

Behavior:
- audio, transcript, workspace, and metrics remain persisted;
- the UI explains that no report was generated because usable meeting evidence was insufficient;
- no success event is emitted;
- Export remains disabled because no `MeetingReport` exists;
- the condition is logged at WARNING with technical detail, not ERROR;
- unrelated technical failures retain their existing error path.

Frozen acceptance: PASS.

## 8. CAT-002 — imported session runtime path
Status: RESOLVED by TASK-065E.

Commit:
`f970d38`
`fix: use canonical path for imported meetings`

Imported and normally recorded meetings now receive the same canonical `RuntimePaths.meetings_root` from application composition. `RecordingSession` remains independent of platform/runtime path resolution.

The contract remains valid when Windows resolves Documents through a corporate OneDrive-backed location.

Frozen one-folder acceptance with an installed-style working directory: PASS.

### Legacy release-safety note
Three imported sessions created before CAT-002 remain under:
`%LOCALAPPDATA%\Programs\Meeting Assistant AI\output`

They are not automatically migrated by current production code. The full legacy `output` tree must be backed up before uninstall or clean-install validation on that user profile. Do not claim these sessions are safe under uninstall. Migration is not part of TASK-065.

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

This meeting was the primary Corporate Acceptance E2E fixture and produced a validated final report with all delivery artifacts. Retain it as corporate runtime evidence.

## 12. CAT-005 — global exact-coverage fragility
Status: RESOLVED by TASK-065C.

Commit:
`1676a79`
`fix: harden global meeting report integrity`

The real fixture proved two distinct G1 exact-partition failures:
- an otherwise-valid consolidation omitted `('risk', 3, 0)`;
- another generation reused a source reference across different consolidated items, making semantic ownership ambiguous.

Final correction:
- missing G1 source references are appended deterministically as standalone items using the canonical source catalog;
- cross-item source reuse raises a dedicated typed exception and discards the ambiguous G1 graph;
- the fallback is a deterministic identity consolidation with one item per canonical source entry;
- malformed, invented, wrong-kind, locally duplicated, or otherwise invalid references remain hard errors;
- exact G1 source coverage and uniqueness are revalidated before G2;
- G2 `source_item_ids` represent only semantic items that actually support their narrative text;
- executive-summary references are not required to enumerate every semantic item and are never fabricated as a coverage checklist.

The final real E2E completed G1, G2, assembly, grounding/report validation, and delivery. The chunk-3 risk survived through source provenance into the final assembled report.

## 13. TASK-065C — Deterministic Global Coverage
Status: CLOSED.

Permanent principle:

`LLM = semantic intelligence`

`Code = integrity, coverage, provenance`

Permanent G1 contract:
1. Let the LLM perform semantic merging and wording.
2. Deterministically append genuinely missing source entries.
3. On ambiguous cross-item reuse, emit a warning and use canonical identity consolidation instead of guessing.
4. Preserve strict validation for malformed or invalid references.
5. Require exact 100% source coverage and one owner per source before G2.

Permanent G2 contract:
1. Narrative references must be integer, non-negative, unique within each grounded text, and resolve to existing semantic items.
2. Title-specific grounding remains mandatory.
3. Executive-summary references describe actual support and may be a valid subset.
4. Structured report sections and G1 coverage own operational completeness; narrative provenance is not global bookkeeping.

The successful staged path still makes exactly two provider calls: G1 and G2. Do not introduce retries as a substitute for deterministic integrity.

## 14. Final TASK-065 acceptance evidence
Broad regression:
- 1018 collected
- 1016 passed
- 2 skipped
- 0 failed

Frozen acceptance:
- CAT-001: PASS
- CAT-002: PASS

The real corporate meeting completed the production-faithful path from the saved corrected transcript through deterministic G1 handling, G2, staged assembly, validators, and artifact delivery.

Verified final artifacts:
- `.mai/meeting_report.json`
- `.mai/action_items.json`
- `.mai/decisions.json`
- `Documentos/Meeting Report.md`
- `Documentos/minutes.docx`
- `Documentos/meeting.pdf`

The CAT-005 risk originating at `('risk', 3, 0)` remained represented through semantic provenance and final report evidence.

## 15. Release-preparation state
Next intended prerelease:
`v0.9.0-alpha.3`

No production change remains required before release metadata preparation. Remaining release work is metadata/version alignment, release notes, a new one-folder build, installer validation, and publication under a new prerelease tag. Do not overwrite or retag `v0.9.0-alpha.2`.

Before uninstall or clean-install validation on the current user profile, back up the complete legacy tree:
`%LOCALAPPDATA%\Programs\Meeting Assistant AI\output`

It contains three imported sessions created before CAT-002 and is not automatically migrated. Do not assume uninstall preserves it.

## 16. First Codex instruction
Read `AGENTS.md` and `docs/CODEX_HANDOFF.md` completely, then inspect the repository and current Git state.

Treat TASK-065 and CAT-001 through CAT-005 as closed unless new evidence proves a regression. The next intended work is `v0.9.0-alpha.3` release preparation; confirm its exact scope before editing release metadata.

Never touch or stage the two protected workflow documents. Do not stage local probes or legacy user data. Preserve the alpha.2 tag and release artifacts.
