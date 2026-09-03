# AGENTS.md — Meeting Assistant AI (MAI)

## Purpose
This repository contains Meeting Assistant AI (MAI), a Windows desktop application for local meeting capture, transcription, meeting intelligence, and deterministic artifact delivery.

Treat this file as the persistent engineering contract for work performed with Codex.

## Working language
- User-facing communication: Spanish.
- Code, identifiers, commit messages, and technical documentation may remain in English where that matches the repository.
- Be direct and technical.

## Repository and production target
- Repository: `remybrioso/MeetingAssistantAI`
- Product code lives primarily under `develop/`.
- Primary production target: constrained corporate Windows workstation.
- Corporate checkout: `C:\Proyectos\MeetingAssistantAI`
- Development directory: `C:\Proyectos\MeetingAssistantAI\develop`
- Python environment: `C:\Proyectos\MeetingAssistantAI\develop\.venv`
- Do not change PowerShell execution policy.
- Prefer `\.venv\Scripts\python.exe` directly; do not assume activation works.

## Engineering standard
All changes must be production-grade.

Do not introduce hacks, silent fallbacks, compatibility shims without an explicit architectural reason, hidden data loss, validation suppression, retry loops as substitutes for deterministic correctness, or unrelated cleanup.

Before modifying code:
1. Inspect the relevant implementation and tests.
2. Explain the exact intended scope.
3. Identify files expected to change.
4. Distinguish root-cause correction from symptom suppression.

Prefer deterministic code for invariants, integrity, provenance, coverage, persistence, and validation. Use the LLM only for genuinely semantic work.

## Git rules
- Never use `git add .`.
- Stage files explicitly by path.
- Never stage or modify unrelated user files.
- Do not create a commit until the current task has passed its required gates.
- Keep separate concerns in separate commits.
- Do not amend an already valid checkpoint merely for cosmetic reasons.
- Do not rewrite published release history.
- Do not retag or overwrite `v0.9.0-alpha.2`.
- The next release after Corporate Acceptance fixes should be a new version, likely `v0.9.0-alpha.3`.
- Before any commit inspect:
  - `git diff --cached --name-status`
  - `git diff --cached --check`
  - `git diff --cached --stat`
  - `git status --short`

Current Corporate Acceptance branch:
`task-065-corporate-acceptance-hardening`

Release baseline:
`c67e32965febfc3e5a9f2dafcb9cbd7a159bf622`
`chore: prepare v0.9.0-alpha.2 release`

Validated Corporate Acceptance HEAD:
`3209fe666b6ce0ae9659494a6ec5a95ae994d83d`

Corporate Acceptance commits:
- `7af7eba` — `fix: harden Ollama structured output contracts`
- `d1ce1db` — `fix: harden temporal transcript integrity`
- `0f17f27` — `docs: add Codex engineering handoff`
- `1676a79` — `fix: harden global meeting report integrity`
- `f970d38` — `fix: use canonical path for imported meetings`
- `b8eeac2` — `test: avoid imported meeting module collision`
- `3209fe6` — `fix: handle insufficient meeting evidence gracefully`

## Files that must not be touched or staged
The following are user-maintained workflow documents and are outside the current product-hardening commits:
- `Meeting Assistan AI_workflow.txt`
- `docs/Meeting_Assistant_AI_workflow_actualizado.txt`

They may appear modified/untracked in `git status`. Leave them alone unless explicitly scoped.

Diagnostic `probe_*` scripts that may exist locally are not automatically release files. Do not stage them unless explicitly scoped.

## Runtime architecture
Production release contract:

Source application
→ PyInstaller one-folder build
→ frozen executable smoke test
→ Inno Setup installer
→ clean/isolated Windows validation

Important constraints:
- Windows GUI build uses PyInstaller one-folder mode.
- Ollama is external at `http://localhost:11434`.
- Production AI model: `qwen2.5:3b`.
- Faster-Whisper model/cache is external.
- CustomTkinter resources are bundled.
- User meetings belong under the canonical user Documents workspace, not under the installed application directory.
- Corporate OneDrive-backed Documents paths are expected.

## Test philosophy
Use the narrowest meaningful test first, then broader regression.

Do not claim the full suite is green unless it actually completed with zero unexpected failures.

Real external Ollama tests are optional and gated by:
`MAI_RUN_REAL_OLLAMA_SCHEMA_TESTS=1`

Corporate acceptance on the real workstation is stronger evidence than a synthetic unit test for environment-specific behavior.

## Current Corporate Acceptance state
Read `docs/CODEX_HANDOFF.md` before performing further work.

TASK-065 Corporate Acceptance is closed at the validated HEAD above:
- TASK-065A — Ollama structured-output compatibility: CLOSED.
- TASK-065B — temporal transcript integrity: CLOSED.
- TASK-065C — global semantic/narrative integrity: CLOSED.
- TASK-065D — broad regression: CLOSED.
- TASK-065E — imported canonical runtime path: CLOSED.
- TASK-065F — insufficient-evidence UX: CLOSED.

CAT-001 through CAT-005 are RESOLVED.

Final broad regression:
- 1018 collected
- 1016 passed
- 2 skipped
- 0 failed

Frozen acceptance:
- CAT-001: PASS
- CAT-002: PASS

The real 35-minute corporate meeting session remains important acceptance evidence. Do not delete it.

## Permanent post-TASK-065 architecture
The governing principle remains:

`LLM = semantic intelligence`

`Code = integrity, coverage, provenance`

Permanent rules:
1. Imported and normally recorded meetings use the same canonical `RuntimePaths.meetings_root`.
2. Faster-Whisper word discontinuities greater than 10 seconds are normalized before downstream chunking.
3. G1 source coverage is reconciled deterministically.
4. Ambiguous cross-item source reuse triggers an explicit deterministic identity consolidation; code must not guess which semantic item owns the reference.
5. G2 executive-summary references describe the semantic items that actually support the text; they are not a checklist for global semantic coverage.
6. Expected insufficient-evidence outcomes use typed domain exceptions and are not technical failures.
7. Export is enabled only when a `MeetingReport` exists.
8. Ollama remains external and `qwen2.5:3b` remains the production model.
9. PyInstaller remains one-folder.
10. Corporate runtime evidence on the real Windows workstation remains the acceptance truth for environment-specific behavior.

## Release preparation and legacy-data safety
- The next intended prerelease is `v0.9.0-alpha.3`.
- No production change remains required before release metadata preparation.
- Three imported sessions created before CAT-002 remain under `%LOCALAPPDATA%\Programs\Meeting Assistant AI\output`.
- Current production code does not automatically migrate that legacy data.
- Back up the full legacy `output` tree before uninstall or clean-install validation on that user profile.
- Do not claim the legacy sessions are safe under uninstall, and do not design a migration unless it is explicitly scoped.
