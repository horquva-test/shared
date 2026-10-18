# Case Study: Mock Failure Simulation for OBA Core

## 1. Objective

This case study documents a mock-first approach for evaluating common operational failures in an organization automation system. The goal is to define expected detection, recovery, and evidence requirements without changing live services.

## 2. Scope and Safety

All scenarios in this case study are synthetic. They cover credential unavailability, a changed source URL, a missing notification channel, an unavailable AI model provider, and a rate-limit response.

No live credentials were disabled, no real Slack channels were deleted, and no production services were modified. The current failure simulation script generates scenario descriptions and checks mock state; it does not independently trigger or verify real failures.

## 3. Scenarios and Expected Responses

### Scenario 1: Credential Unavailable

**Risk:** An automation workflow may fail when a required credential is missing or unavailable.

**Expected response:** Report the affected workflow and credential reference, stop dependent actions safely, and request authorized credential restoration.

**Evidence to collect:** Scenario ID, timestamp, workflow identifier, error message, and recovery result.

### Scenario 2: Source URL Changed

**Risk:** A workflow may read stale data or fail if a configured source URL changes.

**Expected response:** Flag the mismatch, avoid silently accepting an unverified source, and require an authorized configuration update.

**Evidence to collect:** Expected source, configured source, detection result, and validation outcome.

### Scenario 3: Notification Channel Missing

**Risk:** An alert may not reach its intended destination.

**Expected response:** Record the delivery failure, preserve the original event, and identify an approved fallback or manual escalation route.

**Evidence to collect:** Destination reference, simulated error, retry or fallback outcome, and final delivery status.

### Scenario 4: Model Provider Unavailable

**Risk:** An AI-dependent task may stop when its configured model provider is unavailable.

**Expected response:** Return a clear error, avoid presenting an unavailable model response as successful, and use a fallback only when it has been configured and approved.

**Evidence to collect:** Provider identifier, error category, fallback decision, and final task status.

### Scenario 5: Rate Limit Exceeded

**Risk:** Requests may fail when a provider limits request frequency.

**Expected response:** Record the rate-limit response and apply bounded retries with backoff when supported. Avoid uncontrolled retry loops.

**Evidence to collect:** Error category, retry count, delay, and final status.

## 4. Current Test Evidence

The latest local validation was performed on 18 October 2026.

- **Change-simulation tests:** 7/7 automated tests passed.
- **Synthetic change feed:** 20 records generated across four change types.
- **Failure simulation:** 5/5 mock checks passed, with zero failed checks.
- **Execution mode:** `mock_only`.
- **Live services contacted:** No, according to the failure-simulation report.
- **Live services changed:** No, according to the failure-simulation report.

These results confirm that the existing local tests and mock assertions passed. They do not establish that live integrations, platform-level failure detection, alert delivery, fallback behavior, retries, or recovery have been tested successfully.

**Outstanding validation:** End-to-end behavior must remain pending until independently tested in an authorized environment. The watchdog's readiness and any live testing authorization must be confirmed by the responsible owner.

## 5. Key Findings

- Explicit failure scenarios make expected system behavior easier to review.
- Credential and configuration problems should produce actionable, traceable errors.
- Notification failures need an approved escalation path.
- AI provider failures should not silently produce misleading success results.
- Retry behavior should be bounded and documented.
- Evidence should distinguish simulated outcomes from independently verified behavior.

## 6. Recommendations

1. Keep failure tests isolated from production services.
2. Use synthetic identities and mock credentials in demonstrations.
3. Add automated assertions for detection, recovery, and logging.
4. Record timestamps, scenario IDs, expected outcomes, and observed outcomes.
5. Verify any fallback behavior before describing it as operational.
6. Have an authorized reviewer approve changes before integration.

## 7. Conclusion

The current work establishes a documented, mock-first foundation for reviewing five operational failure categories. The scenario generator and existing change-simulation tests provide initial evidence, while end-to-end failure detection and recovery remain to be validated.

This case study does not claim that production failures were injected or that live integrations were tested.
