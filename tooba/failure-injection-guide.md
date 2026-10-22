# Failure Injection Guide — Person 14

**Prepared by:** Tooba Ghaffar
**Role:** Person 14 — Documentation + Failure Scripts
**For:** Affan Ahmed Khan
**Project:** HORQUVA on HORQUVA
**Testing Mode:** Mock-only
**Status:** Documentation and mock validation completed; live testing pending authorization.

## 1. Purpose

This guide explains how to run and validate the mock failure scenarios prepared for the HORQUVA on HORQUVA project.

The scripts simulate failures locally so the team can review expected behavior without changing real accounts, credentials, workflows, integrations, or production data.

**Important:** Passing mock tests does not prove that the live watchdog detects real failures, delivers alerts, or verifies recovery.

## 2. Safety Rules

- Run the scripts in mock mode only.
- Do not remove or modify real employee accounts or credentials.
- Do not change live n8n workflows, Slack webhooks, Entra ID accounts, Jira settings, or other integrations.
- Do not run live failure-injection scenarios without explicit approval from the responsible project lead.
- Never place passwords, API keys, access tokens, or OTPs in scripts, logs, screenshots, or Slack messages.
- Keep mock results separate from live testing results.
- If the environment or authorization is unclear, stop and ask the project lead.

## 3. Prerequisites

Before starting, verify that:

1. The HORQUVA shared repository is available locally.
2. Python is installed and available through the `python` command.
3. You are working on the intended Git branch.
4. The required scripts exist in the `tooba/scripts` directory.
5. The working tree has been checked before generating or modifying files.

Open PowerShell and navigate to the repository root:

```powershell
cd C:\HORQUVA\shared
```

Check the current branch and working-tree status:

```powershell
git status -sb
```

Check that the required files exist:

```powershell
Test-Path .\tooba\scripts\simulate-changes.py
Test-Path .\tooba\scripts\simulate-failures.py
Test-Path .\tooba\scripts\test_simulate_changes.py
```

Expected result: all three commands return `True`.

## 4. Run Change-Simulation Tests

Run the automated tests for the change-simulation script:

```powershell
python -m unittest discover -s .\tooba\scripts -p "test_*.py" -v
```

The previously validated result was **7/7 tests passed**.

These tests validate the local change-simulation logic. They do not test live integrations.

**Pass criterion:** The test process finishes successfully and all tests pass.

**Fail criterion:** Any test reports `FAIL`, `ERROR`, or an unexpected exception. Record the error output and investigate before proceeding.

## 5. Generate Synthetic Change Records

If new synthetic change records are required, run:

```powershell
python .\tooba\scripts\simulate-changes.py
```

The script generates synthetic records for mock testing. The previously validated dataset contained 20 synthetic records.

The simulated change types include:

- Synthetic departure.
- Model swap.
- Credential removal.
- Rate-limit failure.

After running the script, inspect the repository status:

```powershell
git status -sb
```

If the generated CSV has changed, review the changes before deciding whether to keep them:

```powershell
git diff -- tooba/change-feed-ground-truth.csv
```

Only if the CSV change is unwanted, and you have confirmed that it contains no intentional work you need to keep, restore it with:

```powershell
git restore -- tooba/change-feed-ground-truth.csv
```

**Warning:** This restore command discards uncommitted changes to the specified file. Review the diff before using it.

## 6. Run Mock Failure Scenarios

Run the mock failure simulation script:

```powershell
python .\tooba\scripts\simulate-failures.py
```

The script covers five mock scenarios:

| Scenario | Simulated condition |
|---|---|
| Credential unavailable | A synthetic credential is unavailable |
| Source URL changed | A mock source URL changes |
| Notification channel missing | A mock notification destination is unavailable |
| Model provider unavailable | A simulated model provider cannot be reached |
| Rate limit failure | A mock service returns a rate-limit condition |

These scenarios are simulated locally. They do not deliberately cause failures in live services.

The previously validated result was **5/5 mock failure checks passed**.

**Pass criterion:** All five mock checks pass.

**Limitation:** Passing these checks confirms the mock assertions only. It does not prove real platform detection, alert delivery, fallback behavior, retries, or recovery.

## 7. Evidence and Logging

For each validation run, record:

- Date and time, including timezone.
- Name of the person running the test.
- Command executed.
- Expected result and actual result.
- Number of tests passed and failed.
- Scenario names and results.
- Relevant error messages, if any.
- Git branch and commit identifier, when applicable.
- Whether the test was mock-only or live.
- Any unresolved blocker and follow-up action.

Keep logs and screenshots free of secrets and unnecessary personal information.

Do not describe a mock result as proof of live alert delivery, live failure detection, or successful recovery.

## 8. Acceptance Criteria

The mock validation can be considered successful when:

1. The change-simulation tests complete successfully.
2. The mock failure checks complete successfully.
3. The generated records are synthetic.
4. The output contains no unexpected errors.
5. The evidence and limitations are documented.
6. The repository changes have been reviewed.
7. Untested platform-level detection and recovery remain marked as pending.
8. No live platform or production resource is changed.

The previously recorded validation results were:

- Change-simulation tests: **7/7 passed**.
- Mock failure checks: **5/5 passed**.
- Synthetic records: **20**.

These are previously recorded results. Rerun the commands if fresh evidence is required.

## 9. Troubleshooting

**Python command not found**

Check the installed Python version:

```powershell
python --version
```

**File not found**

Confirm that you are in the repository root:

```powershell
cd C:\HORQUVA\shared
```

Check the script locations:

```powershell
Test-Path .\tooba\scripts\simulate-changes.py
Test-Path .\tooba\scripts\simulate-failures.py
```

**Test failure**

Preserve the error output and inspect the relevant test and script before making changes.

**Unexpected Git changes**

Review the working tree before staging or committing:

```powershell
git status -sb
git diff --check
git diff
```

Do not commit unrelated files or overwrite another contributor's work.

**Live integration test requested**

Do not proceed until the project lead confirms the approved environment, test account permissions, authorized failure scenarios, monitoring location, and recovery or rollback procedure.

## 10. Live Testing Status

Live watchdog testing and live failure-injection scenarios remain separate from this guide's mock validation.

The project lead previously reported that the watchdog's mock run generated three alerts for three simulated failures, and a repeat run generated zero duplicate alerts. No messages were posted externally during that mock run.

The following items must remain marked as pending until supported by confirmed evidence:

- Completion of live watchdog testing.
- Live failure detection.
- Delivery of alerts to the configured Slack channel.
- Verification of recovery after a real workflow failure.
- Approval and execution of live failure-injection scenarios.

The watchdog's mock results are the project lead's results and should not be presented as Tooba's independent live test results.

## 11. Handover Note

The mock failure simulation script and its documentation have been prepared for review and handover to Affan Ahmed Khan.

The previously validated mock checks passed: 7/7 change-simulation tests and 5/5 mock failure checks.

The scripts are intended for mock-only validation. No live failure-injection testing should be performed without explicit authorization.

Live detection, alert delivery, and recovery verification must remain pending until confirmed by the responsible project lead.

**Prepared by:** Tooba Ghaffar
**Handover to:** Affan Ahmed Khan
**Status:** Mock documentation and validation completed; live testing and live verification pending authorization and confirmation.
