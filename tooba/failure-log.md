# Failure Simulation Log

**Owner:** Tooba Ghaffar — Person 14  
**Purpose:** Record mock failure scenarios, expected detection, recovery options, and available evidence.  
**Safety:** Mock-only simulations. No live services or credentials were contacted or modified.

## Status Definitions

- **SIMULATED:** The local script generated the scenario record.
- **PENDING VALIDATION:** Detection and recovery behavior has not been independently tested.
- **PASS:** Use only after the expected behavior has been tested and evidence recorded.
- **FAIL:** Use only when a test was executed and the observed behavior did not meet expectations.

## Test Environment

- Script: `scripts/simulate-failures.py`
- Mode: `mock_only`
- Scenarios generated: 5
- Live services contacted: No
- Live services changed: No
- Execution result: Script completed and printed five scenario records.
- Evidence limitation: The current script generates scenario descriptions; it does not connect to real platforms or verify actual workflow detection or recovery.

## Failure Records

### FAIL-001 — Workflow Credential Unavailable

- **Component:** Mock n8n workflow
- **Trigger:** A required workflow credential is unavailable.
- **Expected detection:** The workflow or preflight check identifies the missing credential.
- **Expected recovery:** Restore an authorized test credential or use an approved test fallback.
- **Observed evidence:** The local script generated the scenario record successfully.
- **Status:** SIMULATED; detection and recovery pending validation.
- **Safety note:** No real credential was removed or changed.

### FAIL-002 — Source URL Changed

- **Component:** Mock data source
- **Trigger:** The configured source URL differs from the expected test URL.
- **Expected detection:** URL validation identifies the mismatch.
- **Expected recovery:** Verify the approved test URL and update the test configuration.
- **Observed evidence:** The local script generated the scenario record successfully.
- **Status:** SIMULATED; detection and recovery pending validation.
- **Safety note:** No live source URL was changed.

### FAIL-003 — Notification Channel Missing

- **Component:** Mock Slack notification destination
- **Trigger:** The configured mock notification destination cannot be found.
- **Expected detection:** The notification step reports that the destination is unavailable.
- **Expected recovery:** Select a valid mock or authorized test destination.
- **Observed evidence:** The local script generated the scenario record successfully.
- **Status:** SIMULATED; detection and recovery pending validation.
- **Safety note:** No real Slack channel was deleted or modified.

### FAIL-004 — AI Provider Unavailable

- **Component:** Mock AI provider
- **Trigger:** The mock provider reports that it is unavailable.
- **Expected detection:** A health check or provider call reports an unavailable state.
- **Expected recovery:** Use an approved fallback provider or retry after recovery, subject to policy.
- **Observed evidence:** The local script generated the scenario record successfully.
- **Status:** SIMULATED; detection and recovery pending validation.
- **Safety note:** No live AI provider was contacted.

### FAIL-005 — Rate Limit Exceeded

- **Component:** Mock AI provider
- **Trigger:** The mock provider returns a rate-limit response.
- **Expected detection:** The system recognizes the rate-limit condition.
- **Expected recovery:** Apply bounded backoff and retry within the permitted limits.
- **Observed evidence:** The local script generated the scenario record successfully.
- **Status:** SIMULATED; detection and recovery pending validation.
- **Safety note:** No live API requests were sent.

## Follow-up Actions

1. Add automated assertions for the five scenario records.
2. Test expected detection and recovery behavior using local mocks.
3. Record actual outputs and test results before marking any scenario PASS or FAIL.
4. Give Affan a mock-only failure-injection guide with commands and expected outcomes.
5. Keep credentials, tokens, and secrets out of source control.
