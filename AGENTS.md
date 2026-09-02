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

Known Corporate Acceptance commits:
- `7af7eba` — `fix: harden Ollama structured output contracts`
- `d1ce1db` — `fix: harden temporal transcript integrity`

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

In summary:
- TASK-065A: closed and committed.
- TASK-065B: closed and committed.
- CAT-005: root cause confirmed; next implementation task is TASK-065C.
- CAT-002 and CAT-001 remain open after 065C.
- The real 35-minute corporate meeting session is an important acceptance fixture. Do not delete it.

## TASK-065C architectural principle
The next task must follow:

LLM = semantic intelligence
Code = integrity, coverage, provenance

Do not solve CAT-005 by increasing retries, weakening validation and silently dropping source knowledge, enlarging prompts without evidence, or depending on the model to perform exact reference bookkeeping.

The intended correction is deterministic coverage reconciliation after semantic generation, while continuing to reject malformed, invented, duplicated, or invalid references.

Read `docs/CODEX_HANDOFF.md` for the detailed evidence and proposed scope before modifying anything.
