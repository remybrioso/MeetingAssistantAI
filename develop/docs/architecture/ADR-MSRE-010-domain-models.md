# ADR MSRE-010 — Recovery Experience Domain Models

## Status

Accepted.

## Context

MAI capabilities currently produce technical recovery identifiers such as
`CONFIGURE_SYSTEM_AUDIO`. The UI must not interpret those identifiers or
contain recovery content.

## Decision

Introduce an independent, immutable Recovery Experience domain composed of:

- `Severity`
- `Difficulty`
- `RecoveryStep`
- `HelpLink`
- `AutomaticAction`
- `RecoveryExperience`
- `RecoveryResult`

Domain models have no dependencies on UI frameworks, EventBus, storage,
JSON, logging, or execution services.

## Consequences

- Recovery experiences can be reused by Setup Wizard, System Status,
  Help Center, diagnostics, and future AI-assisted support.
- Content loading and localization remain deferred to MSRE-011.
- Automatic action execution remains deferred to MSRE-013.
- The domain can be tested independently.
