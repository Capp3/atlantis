# ADR 0002 — Pin `PyQt6 < 6.10` to keep macOS 12 working

| Status | Date | Owner |
|--------|------|-------|
| Accepted | 2026-05-06 | Atlantis core team |

## Context

The Atlantis runtime depends on `PyQt6` and `PyQt6-WebEngine`. Starting with the 6.10 series, Qt's macOS wheels require **macOS 13.0+**. The project's reference development host runs **macOS 12.7.6**, which is still a supported deployment target for the MVP.

Symptom: with `PyQt6 == 6.10` installed, running `pytest` failed with `AssertionError: Sorry, "python" cannot be run on this version of macOS. Qt requires macOS 13.0.0 or later, you have macOS 12.7.6.`

## Decision

Pin both runtime dependencies to the 6.7–6.9 range in `pyproject.toml`:

```toml
dependencies = [
    "PyQt6>=6.7.0,<6.10.0",
    "PyQt6-WebEngine>=6.7.0,<6.10.0",
]
```

CI's default Linux job runs `ubuntu-latest`, which is unaffected. A `macos-13` job exists on `workflow_dispatch` only, so we do not burn CI minutes on the macOS path on every PR.

## Consequences

**Positive**

- The MVP is usable on the project's reference host without changing system Qt or upgrading macOS.
- New contributors on macOS 12 get a working environment out of the box.

**Negative**

- We do not pick up bug fixes or features from the 6.10+ Qt line until the pin is relaxed.
- The pin must be revisited when we drop macOS 12 support (or when the upstream LTS pin moves).

## Follow-ups

- Track Qt's macOS minimum-version policy; revisit annually.
- When we drop macOS 12, relax the pin and remove this ADR's mitigation step from the [Troubleshooting page](../user-guide/troubleshooting.md).
