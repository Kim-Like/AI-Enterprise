---
phase: 03-program-and-agent-duplication
plan: 02
subsystem: programs
tags: [programs, payloads, rsync, exclusions]
requires:
  - 03-01
provides:
  - "Copied canonical first-party program payloads into `AI-Enterprise/programs`"
  - "Recorded explicit payload exclusions and SSH-first placeholder handling"
  - "Added payload verification tests for canonical roots and excluded junk"
affects: [phase-3, programs, payloads]
tech-stack:
  added: [rsync]
  patterns: [filtered copy, exclusion contract, placeholder preservation]
requirements-completed: [DUP-03, AGT-02]
duration: 25min
completed: 2026-03-08
---

# Phase 3 Plan 02: Duplicate first-party program payloads Summary

**Copied the canonical first-party program payload tree into the clean target with deterministic exclusions for nested repos, dependency caches, WordPress noise, and orphan Samlino incubators.**

## Verification

- `pytest -p no:cacheprovider tests/test_program_payloads.py -q`: pass
- payload exclusion scan: pass

## Self-Check

PASSED - canonical program roots exist in the clean target and excluded junk remains absent.

---
*Phase: 03-program-and-agent-duplication*
*Completed: 2026-03-08*
