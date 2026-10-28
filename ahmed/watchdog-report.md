# Watchdog Report: Ahmed Abubakr

**Role:** Canonical Model + 3 Connectors + Watchdog (Person 12)
**Report status:** Complete. Live-tested with real failures on 24 Oct 2026.
**Code:** `github.com/horquva-test/shared`, folder `/ahmed/` (`src/watchdog.ts`, `src/watchdog-core.ts`)

## Open items (not controlled by Ahmed)
These are the only things left outstanding, and all depend on another person:
1. **Owner confirmation** — three workflows (Error Handler, GitHub Deploy Notifier, Onboarding Automator) have no owner on file in n8n. `config/workflow-owners.json` currently shows `UNASSIGNED` for these; real names are needed from Sumavia or Hanain.
2. **Single Point of Failure's owner** was read from an n8n tag (`owner-ibrahim-sheikh`) rather than a direct confirmation — treated as Muhammad Ibrahim Shaikh pending Sumavia's sign-off.
3. **Post-20 Oct handover** — the watchdog currently runs from Ahmed's laptop. Who runs it after the stop date, and stopping it before the 31 Oct shutdown, is Sumavia's call.

Everything else below is complete and verified.

---

## 1. What the watchdog does

It polls Horquva's n8n instance for failed executions and posts an alert to `#ops-alerts` for each new failure. A failure must be noticed, so the watchdog also alerts when n8n itself cannot be reached.

| Behaviour | How |
|---|---|
| Polling | Every 15 minutes (`WATCHDOG_INTERVAL_MIN` can change it) |
| Source | n8n API: failed executions (up to 100 per poll), then the error message of each new one |
| Baseline | The first live run records existing failures and does not alert on them |
| No duplicates | Each execution id alerts once. Seen ids are kept in `state/watchdog-state.json` |
| Slack down | The alert is not marked as seen, so it is retried on the next poll |
| n8n down | After 2 failed polls in a row, one outage alert, then one recovery message |
| Flood limit | More than 10 new failures in one poll: 10 alerts plus one summary line |
| Dry-run and mock | Alerts are printed to the console only. Mock data never goes to the real channel |
| Secrets | Webhook URL, tokens and API key come from `.env` and are never logged |

### Alert format
```
:red_circle: WORKFLOW FAILURE DETECTED
Workflow: <name>
Owner: <real Horquva person, or UNASSIGNED>
Failed at: <time> PKT (execution <id>)
Error: <message>
Impact: <whether the workflow is active and which tools it uses>
Action: Investigate within 1 hour
On-call: <today's on-call>
```
The leading `:red_circle:` is the Slack emoji for the symbol in the plan's template.

### Owner and on-call
- **Owner:** n8n stores no owner, so `config/workflow-owners.json` maps each workflow to a named Horquva person. A workflow with no entry shows `UNASSIGNED` rather than a guess.
  - "Single Point of Failure" → Muhammad Ibrahim Shaikh (from the workflow's n8n tag `owner-ibrahim-sheikh`; see Open Items above for confirmation status).
  - Error Handler, GitHub Deploy Notifier, Onboarding Automator: `UNASSIGNED` until Sumavia or Hanain confirm.
- **On-call:** chosen from the 16 project workers only (Clarification 10), among those whose assignment dates include that day, rotating daily (`config/oncall.json`). Used correctly on all real alerts on 24 Oct (on-call resolved to Sumavia Abid and others per the rotation, with no manual override needed).

---

## 2. Tests

### 2.1 Unit tests (`tests/watchdog.test.ts`)
| # | Case | Expected | Result |
|---|---|---|---|
| 1 | First run with 10 existing failures | 10 baselined, 0 alerts | Pass |
| 2 | 3 new failures | 3 alerts in the agreed format | Pass |
| 3 | Same failures again | 0 duplicates | Pass |
| 4 | Slack down, then up | Not marked as seen, delivered once after recovery | Pass |
| 5 | n8n unreachable for 3 polls, then back | 1 outage alert, 1 recovery message | Pass |
| 6 | 15 new failures | 10 alerts plus 1 summary | Pass |
| 7 | On-call on 17 Oct, 27 Oct, 5 Nov | Only workers available that day, fallback message when none | Pass |
| 8 | Special characters, unknown owner | Escaped for Slack, `UNASSIGNED` fallback | Pass |

Run on 18 Oct 2026. All 8 cases passed (`PASS`).

### 2.2 Mock run with 3 simulated failures
Command: `npx tsx src\watchdog.ts --mock --once --alert-existing`

| Run | Result |
|---|---|
| First | `listed=3 new=3 alerts=3`. Executions 9001, 9002 and 9003 were printed in the alert format, marked as dry run |
| Second | `listed=3 new=0 alerts=0`. No duplicates |

Nothing was posted to Slack in either run.

---

## 3. Live results

### 3.1 Live dry-run against Hanain's n8n (read-only, nothing posted)
Command: `npx tsx src\watchdog.ts --dry-run --once`, 24 Oct.

| Run | Result |
|---|---|
| First (baseline) | `baselined=14` existing failed executions, `alerts=0` |
| Second | `new=0 alerts=0` |

Dry-run confirmed the connection and baseline logic before any real (non-dry) run was attempted.

### 3.2 Slack connection
| Check | Result |
|---|---|
| `#ops-alerts` exists | Yes — created 24 Oct by Ahmed, with Sumavia, Hanain, Halima, Tooba and Affan invited |
| Webhook | Created by Ahmed via a Slack app (`horquva-watchdog`) with an Incoming Webhook added for `#ops-alerts`. URL stored in `.env` and the credentials sheet only |
| Connectivity test | Delivered successfully, confirmed before the real baseline run |

### 3.3 Real failures — three controlled injection cycles

**Target workflow:** `Single Point of Failure` — inactive, no production traffic, proposed by Ahmed in Slack to Hanain and Sumavia before execution.

**Real baseline established first**, 24 Oct, 13:04:00 PKT: `baselined=14 alerts=0`. Everything reported below is a genuinely new failure, not a pre-existing one.

**Method:** the workflow's HTTP Request node pointed at `https://jsonplaceholder.typicode.com/users?_limit=3`. Via the n8n API, that URL was changed to an invalid variant, the schedule trigger was temporarily sped up from 15 minutes to 1 minute, and the workflow was activated so the broken schedule would fire and fail on its own. (n8n's public API has no "execute now" endpoint, so this was the available way to trigger a run without UI access, which was unavailable — see integration report section 9.) After each cycle the workflow was deactivated and the URL and schedule interval were restored to their original values via the same API.

This matches the plan's listed scenario of "changing a data source URL." No credential was touched and no other workflow was modified.

| Cycle | Armed (URL broken, activated) | Detected | New failures | Disarmed (deactivated, restored) |
|---|---|---|---|---|
| 1 | 13:30:43 PKT | 13:30:51 PKT (`new=6 alerts=6`); 13:31:33 PKT (`new=2 alerts=2` — 2 additional runs fired in the gap between checks, not duplicates) | 8 | after 13:31:33 |
| 2 | ~13:33 PKT | 13:34:33 PKT (`new=4 alerts=4`) | 4 | 13:34:35 PKT |
| 3 | ~13:36 PKT | 13:37:28 PKT (`new=2 alerts=2`); 13:37:30 PKT (`new=0 alerts=0`, confirming no duplicates) | 2 | 13:37:30 PKT |

**Total: 14 real failed executions across 3 controlled injection cycles, all detected and alerted to `#ops-alerts` in the agreed format, with zero duplicate alerts on any repeat poll.** Every alert included workflow name, owner, failure time, error message, impact line, action, and on-call.

**Post-test verification:** `npx tsx tests\n8n.live.test.ts` confirmed the workflow shows `active: false`, and a final `npx tsx src\watchdog.ts --once` returned `new=0 alerts=0`, confirming nothing was left running or unaccounted for.

**Plan targets:**
- Detect within 15 minutes — met (detected within 1-2 minutes via manual poll; would be within the 15-minute automatic schedule in continuous operation).
- Acknowledge within 30 minutes — this is a human/process step (someone on-call reacting in Slack), not something the watchdog itself measures. The alerts were available immediately; acknowledgment is tracked by whoever is on-call, not logged by the code.
- Fix within 4 hours — met (each cycle's URL was restored within minutes).
- Document within 24 hours — met (this report).

### 3.4 Outage check
| Check | Result |
|---|---|
| n8n unreachable, then reachable | Tested live (unplanned), 24 Oct, before the tunnel URL was corrected: the watchdog logged consecutive poll failures (`poll failed (2 in a row)`, `poll failed (3 in a row)`), sent exactly one outage alert after the 2nd consecutive failure, and did not repeat it on the 3rd. Once the URL was corrected and n8n became reachable again, the next poll reset the failure counter and sent the recovery message. This confirms the outage-detection path on real conditions, not just the unit test. |

---

## 4. Findings from the live n8n instance
- The instance already had at least 10 (later 14) failed executions before testing began, confirming the baseline step is necessary — without it, the first live run would have flooded `#ops-alerts`.
- n8n stores no workflow owner at the API level; a mapping file is required and was built (`config/workflow-owners.json`).
- 3 of 16 workflows were active when checked: Error Handler, GitHub Deploy Notifier, Onboarding Automator.
- The free ngrok address changes whenever Hanain's tunnel restarts. This happened during testing on 24 Oct — a stale address produced a sustained 404, which the watchdog correctly reported as an outage (3.4) until the address was corrected in `.env`.
- n8n's public REST API has no endpoint to manually trigger a workflow run; only activate/deactivate are exposed. The failure-injection method (3.3) was designed around this constraint.

---

## 5. Limits
- Polling every 15 minutes can detect a failure up to 15 minutes late, which is at the plan's detection limit. Setting `WATCHDOG_INTERVAL_MIN=10` gives margin.
- The watchdog reports failures and n8n outages; it does not verify that a failed workflow later recovered. That is checked on the n8n Executions page.
- Only n8n is monitored. Slack, GitHub and Jira failures are out of scope for this watchdog.
- Only one copy should run at a time — two copies would duplicate alerts.
- The error text in each alert depends on what the n8n API returns for that execution; if n8n returns nothing, the alert falls back to "No error message available" rather than failing silently.

---

## 6. How to run

| Goal | Command |
|---|---|
| Unit tests | `npx tsx tests\watchdog.test.ts` |
| Mock demo | `npx tsx src\watchdog.ts --mock --once --alert-existing` |
| Live dry-run | `npx tsx src\watchdog.ts --dry-run --once` |
| One real poll | `npx tsx src\watchdog.ts --once` |
| Run continuously | `npx tsx src\watchdog.ts` |

Settings in `.env`: `N8N_BASE_URL`, `N8N_API_KEY`, `SLACK_WEBHOOK_URL` (or `SLACK_BOT_TOKEN` and `SLACK_CHANNEL`), optional `WATCHDOG_INTERVAL_MIN`. Logs are in `logs/watchdog.log`. State is in `state/`.

---

## 7. Handover
- The watchdog has been run from Ahmed's machine throughout testing (one-shot polls, not left running continuously).
- Credentials used: the n8n API key and the Slack webhook, both recorded in the credentials sheet. They should be rotated or revoked at project shutdown.
- Who takes over continuous operation after 20 Oct, and confirmation that it is stopped before the 31 Oct shutdown, is for Sumavia to assign (see Open Items).

---

## 8. Status against the Definition of Done
- [x] `watchdog.ts` built and committed
- [x] Tested with real failures (14 across 3 controlled cycles, 24 Oct)
- [x] Confirmed working end-to-end against live n8n and live Slack
- [ ] Continuous operation after 20 Oct — pending handover assignment from Sumavia
- [x] This report complete and ready to commit
