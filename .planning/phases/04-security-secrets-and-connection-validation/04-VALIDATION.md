---
phase: 4
slug: security-secrets-and-connection-validation
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-08
---

# Phase 4 - Validation Strategy

> Validation contract for hardening auth/secrets and adding redacted connection status in `AI-Enterprise`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell verification + pytest |
| **Config file** | `AI-Enterprise/.env.example`, `AI-Enterprise/SECRETS-MANIFEST.md` |
| **Quick run command** | `test -f /Users/IAn/Agent/AI-Enterprise/api/security/admin_auth.py && test -f /Users/IAn/Agent/AI-Enterprise/api/routes/settings.py && test -f /Users/IAn/Agent/AI-Enterprise/api/routes/datastores.py && test -f /Users/IAn/Agent/AI-Enterprise/tests/api/test_security_auth.py && test -f /Users/IAn/Agent/AI-Enterprise/tests/api/test_connection_status.py` |
| **Full suite command** | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_runtime_foundation.py tests/api/test_registry_contracts.py tests/api/test_security_auth.py tests/api/test_connection_status.py -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick command
- **After every plan wave:** Run the full suite command
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | SEC-01 | config/auth | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_security_auth.py -q -k default_admin` | yes | green |
| 4-01-02 | 01 | 1 | SEC-02 | settings auth | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_security_auth.py -q -k settings` | yes | green |
| 4-01-03 | 01 | 1 | SEC-01 | manifest | `test -f /Users/IAn/Agent/AI-Enterprise/SECRETS-MANIFEST.md && grep -q \"ANTHROPIC_API_KEY\" /Users/IAn/Agent/AI-Enterprise/SECRETS-MANIFEST.md && ! grep -q \"change-me-admin-key\" /Users/IAn/Agent/AI-Enterprise/.env.example` | yes | green |
| 4-02-01 | 02 | 2 | SEC-03 | status route | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_connection_status.py -q -k status` | yes | green |
| 4-02-02 | 02 | 2 | VAL-01 | datastore verify | `cd /Users/IAn/Agent/AI-Enterprise && PYTHONPATH=/Users/IAn/Agent/AI-Enterprise python3 -m pytest -p no:cacheprovider tests/api/test_connection_status.py -q -k datastore` | yes | green |
| 4-02-03 | 02 | 2 | SEC-01 | no client-side secret pattern | `cd /Users/IAn/Agent/AI-Enterprise && python3 - <<'PY'\nfrom pathlib import Path\nroot = Path('/Users/IAn/Agent/AI-Enterprise')\npaths = [root / 'api', root / 'src', root / 'frontend']\nfor base in paths:\n    if not base.exists():\n        continue\n    for path in base.rglob('*'):\n        if path.suffix not in {'.py', '.ts', '.tsx', '.js', '.jsx', '.html', '.css'}:\n            continue\n        text = path.read_text(errors='ignore')\n        assert 'localStorage' not in text, path\nprint('OK')\nPY` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Phase 4 starts from an AI-Enterprise baseline that already has runtime, registry, agents, and programs duplicated but no hardened security route surface yet.

---

## Manual-Only Verifications

- Review that secret-status payloads contain only metadata and evidence, never values.
- Review that `partial` vs `live` connection states are used honestly rather than cosmetically.
- Review that the root `SECRETS-MANIFEST.md` matches the clean target's env contract.

---

## Validation Sign-Off

- [x] All tasks have automated verification
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers current baseline and new artifacts
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-08
