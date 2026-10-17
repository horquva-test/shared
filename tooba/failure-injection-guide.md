# Failure Injection Guide

**Prepared by:** Tooba Ghaffar — Person 14  
**For:** Affan Ahmed Khan  
**Purpose:** Run controlled mock failure scenarios and record evidence.

## 1. Safety Rules

- Run the supplied scripts locally from the repository root.
- Use mock data only.
- Do not delete real Slack channels or disable real credentials.
- Do not modify live n8n workflows, production URLs, real accounts, or API keys.
- Never put passwords, tokens, or secrets in logs or source control.
- The supplied failure script generates simulated scenario records. It does not inject failures into live platforms or prove that a real workflow can recover.

## 2. Prerequisites

- Python installed and available through the `python` command.
- Repository checked out locally.
- Work from the repository root, where the `tooba` directory exists.

Check Python:

```powershell
python --version
```

Check the relevant files:

```powershell
Test-Path .\tooba\scripts\simulate-changes.py
Test-Path .\tooba\scripts\simulate-failures.py
Test-Path .\tooba\change-feed-ground-truth.csv
```

Expected: all three commands return `True`.

## 3. Run the Change Simulation Tests

```powershell
python -m unittest discover -s .\tooba\scripts -p "test_*.py" -v
```

**Expected MVP result:** all seven existing change-simulation tests pass.

**Pass criterion:** the test process finishes with `OK`.

**Fail criterion:** any test reports `FAIL`, `ERROR`, or an unexpected exception. Record the full error output and investigate before proceeding.

## 4. Generate the Synthetic Change Feed

```powershell
python .\tooba\scripts\simulate-changes.py
```

**Expected MVP result:**
- 20 synthetic change records are written.
- Four change types are present: synthetic departure, model swap, credential removal, and rate-limit failure.
- The output confirms mock-only operation.

**Pass criterion:** the script completes and reports 20 records.

**Fail criterion:** the script crashes, produces an unexpected record count, or generates records that are not mock-only.

## 5. Run the Mock Failure Scenarios

```powershell
python .\tooba\scripts\simulate-failures.py
```

**Expected MVP result:** five mock failure scenarios are checked. The latest verified local run reported five mock checks passed (5/5), zero failed checks, and confirmed that no live services were contacted or changed.

**Pass criterion:** all five local mock checks pass. This confirms the mock assertions only; it does not prove real platform detection or recovery.

| ID | Scenario | Expected detection to validate |
|---|---|---|
| FAIL-001 | Workflow credential unavailable | Missing credential is reported |
| FAIL-002 | Source URL changed | URL mismatch is reported |
| FAIL-003 | Notification channel missing | Destination is reported unavailable |
| FAIL-004 | AI provider unavailable | Provider unavailable state is reported |
| FAIL-005 | Rate limit exceeded | Rate-limit response is recognized |

The current script only generates these scenario records. It does not yet test actual detection, fallback, retries, or recovery. Do not mark those behaviors as passed until separate tests provide evidence.

## 6. Evidence to Record

For each run, record:

- Date and time
- Person running the test
- Command executed
- Expected result
- Actual result
- Pass, fail, or pending validation
- Relevant console output or sanitized screenshot
- Follow-up action

For the current local run, record the verified result as 5/5 mock checks passed only if the console output confirms it. Live platform detection, notification delivery, and recovery remain pending validation until independently tested in an authorized test environment.
Do not include secrets or personal access tokens in evidence.

## 7. Acceptance Criteria

The mock exercise is complete when:

1. The existing change-simulation tests pass (latest verified result: 7/7).
2. The change feed contains 20 synthetic records, verified using a read-only count.
3. All five mock failure checks pass (latest verified result: 5/5).
4. Outputs and limitations are documented.
5. Any untested platform-level detection or recovery behavior remains marked pending validation.
6. No live platform or production resource is changed.

## 8. Troubleshooting

**Python command not found:** install or configure Python and reopen PowerShell.

**File not found:** check that the terminal is in the repository root and that the `tooba` directory exists.

**Test failure:** preserve the error output and inspect the relevant test and script before changing code.

**Unexpected Git changes:** run `git status -sb` and review the diff before staging or committing anything.

## 9. Final Report

Summarize the commands run, the test results, the evidence collected, unresolved issues, and any recommendations. Clearly distinguish a generated mock scenario from a verified system failure and recovery.
