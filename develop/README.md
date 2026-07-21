# MAI — MSRE-010 Sprint 10.1

Recovery Experience domain models for Meeting Assistant AI.

## Install development dependency

```bash
python -m pip install -r requirements-dev.txt
```

## Run tests

```bash
python -m pytest
```

## Integration

Copy `application/recovery` into the MAI repository while preserving the
package structure. No existing MAI module must import UI or infrastructure
into these domain models.
