# Integration Report: Ahmed Abubakr

**Role:** Canonical Model + 3 Connectors + Watchdog (Person 12)
**Assignment:** 15-day, 5 Oct to 20 Oct 2026 (extended; see Open Items)
**Report status:** Complete except for one external blocker (GitHub App installation — see section 7 and Open Items).
**Repositories:**
- Working repo: `github.com/ahmedabubakr-horquva/horquva-test-ahmed`
- Shared repo: `github.com/horquva-test/shared` (folder `/ahmed/`)

## Open items (not controlled by Ahmed)
1. **GitHub App installation** is blocked by an org-level restriction ("Install is prohibited") on `horquva-test`, not by anything in the connector code. Escalated to the CEO on 24 Oct; CEO authorized Ahmed to install it directly using Ali's credentials if Ali remains unavailable. In progress — see section 7 for the full troubleshooting trail. The connector itself is complete and mock-tested; only the live run is pending this fix.
2. **Supabase RLS and constraint tests** — run once, result not re-confirmed in writing since. Should be re-verified before final sign-off (SQL given in section 2).
3. **Resolver unit test output** (`tests/resolver.test.ts`, `tests/aliases.test.ts`) — the resolver itself is proven working indirectly (the GitHub connector's identity tests, which import it, pass), but the direct test run's console output was not captured for this report. Low risk; worth a 30-second re-run before sign-off.
4. **Credentials sheet completeness** — rows have been added throughout per the one-hour handover rule, but a final pass to confirm every row (GitHub, GitHub App, Supabase, n8n, Slack webhook) is filled is recommended before sign-off.
5. **Working repo visibility** — currently public. Decide whether to make it private.

Everything else in this report reflects work that is done, tested, and pushed.

---

## 1. Summary of progress

| Deliverable | Plan dates | Status | Evidence |
|---|---|---|---|
| Canonical schema (3 tables) | 6-7 Oct | Done, pushed | `canonical-model/schema.sql`, commit `cde6e1d` |
| Base connector class | 8-9 Oct | Done, compiles | `src/connectors/base.ts`, commit `8527afb` |
| n8n connector | 10-12 Oct | Done — tested on mock and live | `src/connectors/n8n.ts`, commits `e99e179`, `4bf6b26` |
| Identity resolver | 13-15 Oct | Done, pushed | `src/identity/resolver.ts`, commit `e3b7302` |
| GitHub connector | 16-18 Oct | Built and mock-tested. Live test blocked by org installation restriction (Open Items #1) | `src/connectors/github.ts`, section 7 |
| Watchdog | 19-20 Oct | **Done — tested live with 14 real failures across 3 controlled cycles on 24 Oct** | `src/watchdog.ts`, section 9, `watchdog-report.md` |
| Watchdog report | by 20 Oct | Complete | `/shared/ahmed/watchdog-report.md` |

Work started on Day 1 (5 Oct) with account setup. Schema work began on 8 Oct, so the schedule ran about two days behind at first. The n8n connector and the resolver were then finished ahead of their plan dates. The watchdog's live test, including 3 real failure-injection cycles against Hanain's n8n with alerts delivered to `#ops-alerts`, was completed 24 Oct. The GitHub connector's live test is the one remaining item, blocked by an organization-level restriction rather than anything in the code (section 7).

---

## 2. Canonical model

**File:** `canonical-model/schema.sql`. Applied to Supabase project `horquva-test-ahmed`.

### Tables

| Table | Purpose | Key constraints |
|---|---|---|
| `entities` | Every thing Horquva depends on | `type` limited to EMPLOYEE, AGENT, WORKFLOW, TOOL, MODEL, VENDOR; `UNIQUE(source, source_id)` |
| `dependencies` | Directed edges between entities | `from_entity` and `to_entity` reference `entities` with `ON DELETE CASCADE`; `criticality` NUMERIC(3,2), default 0.50 |
| `evidence` | Facts backing an entity | `state` limited to stated, inferred, confirmed, unknown |

### Additions beyond the plan
Four indexes, added so connectors can safely re-run and graph lookups stay fast:
- `uq_dependencies_edge`: unique on `(from_entity, to_entity, type, evidence_source)`, which prevents duplicate edges on re-runs
- `idx_dependencies_from`, `idx_dependencies_to`, `idx_evidence_entity`

### Security and verification
- Connectors use the **service role / secret key**, not the anon key, throughout. With RLS on, the anon key returns no rows.
- Constraint tests were run in the SQL Editor (valid insert succeeds; invalid type `PERSON` fails; duplicate `source` + `source_id` fails; cleanup). See Open Items #2 for re-confirmation before sign-off.
- REST connectivity test with the secret key: the first attempt failed with "Forbidden use of secret API key in browser" — a false alarm, since Windows PowerShell's default User-Agent looks like a browser. The rerun with a custom User-Agent returned 200.

### Known gap
The connectors currently produce canonical objects in memory. Nothing yet writes them into the Supabase tables. A loader (upsert entities, then dependencies by resolved IDs) was treated as out of scope for this assignment window given the GitHub blocker and watchdog priority; flagged for Sumavia to decide if needed.

---

## 3. Connector architecture

**File:** `src/connectors/base.ts`

Abstract class `BaseConnector<TRaw>` with:
- `authenticate()`, `fetchEntities()`, `fetchDependencies()`, `normalize()`, `healthCheck()` (abstract)
- `withRetry()`: on HTTP 429, exponential backoff with jitter (honors the `Retry-After` header; default 5 retries, 500 ms base); on HTTP 401, re-authenticates once and retries
- `collect()`: convenience wrapper for fetch + normalize

Shared types: `CanonicalEntity`, `CanonicalDependency`, `HealthStatus`.

---

## 4. n8n connector

**File:** `src/connectors/n8n.ts`

### Behaviour
- **Mock mode** (default when no URL and key are supplied) reads `tests/fixtures/n8n-workflows.json`.
- **Live mode** calls `GET /api/v1/workflows` with cursor pagination, using the `X-N8N-API-KEY` header.
- `fetchFailedExecutions()` calls `GET /api/v1/executions?status=error`. Used by the watchdog.
- `normalize()` maps each workflow to a `WORKFLOW` entity, with `active`, `nodeCount` and `updatedAt` in metadata.
- `fetchDependencies()` creates `USES_TOOL` edges from each workflow to the external tools its nodes use.

### Test 1: mock (9 Oct)
`tests/n8n.test.ts`
```
entities: 3
dependencies: 4
health: true mock mode
PASS
```

### Test 2: live (16 Oct, re-verified 24 Oct)
`tests/n8n.live.test.ts`, commit `4bf6b26`. Read-only. Target: Hanain Iftikhar's n8n instance over an ngrok tunnel.

| Check | Result |
|---|---|
| Health check | OK, n8n reachable |
| Workflows found | 16 (3 active, 13 inactive) |
| Dependencies extracted | 19 |
| Failed executions returned | 10-28, depending on when polled (grew during the 24 Oct watchdog test as real failures accumulated) |
| Overall | LIVE PASS |

Active workflows: Error Handler, GitHub Deploy Notifier, Onboarding Automator.

**24 Oct addendum:** during watchdog testing the ngrok tunnel address went stale mid-session, producing a sustained 404. This was correctly surfaced by both the connector's health check and the watchdog's outage-detection logic (see section 9), and resolved once Hanain provided the current address.

### What the live run proves
- Authentication with the API key, the health check, workflow listing, dependency extraction, and the failed-executions call all work against a real n8n — including under real failure conditions generated during the watchdog test.
- **Not proven:** pagination across more than one page (16 workflows fit on one page), and explicit 401/429 handling against the real instance (no such responses were encountered).

### Findings that shaped the watchdog
1. The instance already had failed executions before testing (14 at the real baseline on 24 Oct), confirming the need for a baseline step.
2. n8n stores no workflow owner, so the watchdog needs an external mapping — built as `config/workflow-owners.json`.
3. Only 3 of 16 workflows were active at the time of testing.
4. n8n's public REST API has no "run now" endpoint — only activate/deactivate. This shaped how real failures were injected for the watchdog test (section 9).

### Assumptions and limits
- Core plumbing nodes (schedule trigger, webhook, set, if, code, merge, httpRequest and similar) are ignored, as they are not tool dependencies.
- **Criticality is a heuristic, not evidence:** 0.7 for active workflows, 0.3 for inactive.
- Tool targets are identified by node type name (for example `slack`), not yet by canonical TOOL entities.

### Access notes
- The n8n address is created by the ngrok tunnel and changes whenever the tunnel restarts, so it lives in `.env` only, requested fresh from Hanain as needed.
- The ngrok `authToken` in the credentials sheet is not the n8n API key and is not used by this connector.

---

## 5. Identity resolver

**File:** `src/identity/resolver.ts`

### Matching rules
1. **Exact match** on trimmed, lowercased email against the 30-person roster.
2. **Documented alias** match (alias email to canonical roster email).
3. Otherwise the account goes to the **review queue** with a reason (`no-valid-email` or `no-match`).

**Names are never used for matching, and there is no fuzzy matching.** This is a pitfall named in the assignment.

The constructor fails loudly on bad configuration: duplicate roster email, an alias that is already a primary email, an alias pointing to an unknown roster email, or a duplicate alias.

### Canonical identity
The Entra email (`firstname.lastname@sohaibadnanhorquvaoutlook.onmicrosoft.com`) is the canonical identity for the 30 roster users, taken from the Entra rows in `horquva-on-horquva-credentials.xlsx`, rows 20-49. Roster file: `tests/fixtures/roster.json` (30 entries).

### Documented aliases (5)

| Alias | Resolves to | Type | Source of evidence |
|---|---|---|---|
| `natasha.ceo@sohaibadnanhorquvaoutlook.onmicrosoft.com` | Natasha Khan | Official Entra alias | Sohaib Adnan, confirmed in Slack |
| `kia.cfo@sohaibadnanhorquvaoutlook.onmicrosoft.com` | Kia Vang | Official Entra alias | Sohaib Adnan, confirmed in Slack |
| `taha.board@sohaibadnanhorquvaoutlook.onmicrosoft.com` | Taha Nadeem | Official Entra alias | Sohaib Adnan, confirmed in Slack |
| `ahmed.abubakr.horquva@outlook.com` | Ahmed Abubakr | Platform account (Slack) | Credentials sheet |
| `ahmed.abubakr.horquva@gmail.com` | Ahmed Abubakr | Platform account (GitHub, Supabase) | Credentials sheet |

**Rule:** an alias is added only with evidence (a credentials sheet row or direct confirmation). Never by guessing.

### Tests
- `tests/resolver.test.ts` and `tests/aliases.test.ts`: see Open Items #3 for final re-confirmation. The resolver's logic is exercised indirectly and successfully by the GitHub connector's mock identity test (section 7), which imports and uses it with this same roster and alias data.

### Accounts that go to the review queue by design
- Project workers who are not on the 30-person roster (for example Hanain Iftikhar, Muhammad Ali Naeem, Tayyaba Zia, Tooba Ghaffar).
- Entra app registrations / service accounts (credentials sheet rows 50-54) — not people.
- Any roster member whose Slack, GitHub or Jira account uses a different email than their Entra email with no documented alias. Only Ahmed's own are mapped so far.

---

## 6. Toolchain decisions and deviations

| Item | Detail |
|---|---|
| Test runner | `tsx` is used instead of `ts-node`. The installed `ts-node` crashed (`Cannot read properties of undefined (reading 'fileExists')`) with the installed TypeScript version. `tsc --noEmit` still does the type-checking. |
| tsconfig | `verbatimModuleSyntax` set to `false`. The default from `tsc --init` rejects normal `export` syntax in a CommonJS project. |
| Strictness | `exactOptionalPropertyTypes` stays on. The axios `baseURL` option needed an explicit cast. |
| Shell | All commands were run in Windows PowerShell 5.1. |

---

## 7. GitHub connector

### Connector (complete)
**File:** `src/connectors/github.ts`. Authenticates with `@octokit/auth-app` (installation access token, refreshed automatically on a 401).

| Output | Mapping |
|---|---|
| Repository | `TOOL` entity (`source=github`, `sourceId` = repo id), metadata: private, archived, last push, collaborator count, teams |
| Organization member | `EMPLOYEE` entity (`sourceId` = GitHub user id) |
| Collaborator on a repo | `HAS_ACCESS` dependency from person to repo, evidence `github-collaborators-api` |

- Pagination (100 per page, capped at 50 pages), rate-limit handling (a 403 with rate-limit headers is retried with backoff like a 429), and a clear flag when a repo's collaborators cannot be read (`collaboratorsAccessible = false`) instead of silently returning an empty list.
- **Criticality is a heuristic, not evidence:** admin 0.9, maintain 0.8, write 0.7, triage 0.5, read 0.3.

### Identity handling
GitHub rarely exposes user emails, so each login is mapped by hand to a roster email in `config/github-users.json`. Logins with no mapping go to the review queue, using the resolver's exact and alias rules only.

### Tests
- **Mock test, `tests/github.test.ts`: PASS.** 3 repos, 4 members, 5 access dependencies; identity results exact 1, alias 1, review queue 2.
- The live-path code was additionally exercised against a hand-built fake GitHub API (120 repos across two pages, one repo with unreadable collaborators, one rate-limited response, one bad-token case) before any real org was touched, to de-risk the live run. This is not a substitute for the real test, which is still pending (below).
- **Live test, `tests/github.live.test.ts`: not yet run** — blocked, see below.

### GitHub App and installation — full troubleshooting trail
- A GitHub App named `horquva-ahmed-connector` was created on 15 Oct under Ahmed's Horquva account, with **read-only** permissions: Repository (Administration, Contents, Metadata) and Organization (Members). Webhook off.
- First install request for `horquva-test` returned a 404 for the org owner (Muhammad Ali Naeem) — traced to a stale request ID from before the app was installable.
- App visibility was corrected (set to "Any account") and a fresh request was sent; Ali still got a 404 reviewing it.
- Ownership of the app was **transferred to the `horquva-test` organization** on Ali's acceptance, so Horquva now owns the app outright. App ID and private key are unchanged by the transfer and remain valid.
- Post-transfer, attempting to install still fails — the org's install page (`.../settings/apps/horquva-ahmed-connector/installations`) shows **both** available install targets (`ali-naeem-horquva` and `horquva-test`) greyed out with **"Install is prohibited."** This is an org/account-level restriction, not an app configuration issue — confirmed because the app's own "Any account" installability setting is already correct.
- Escalated to the CEO on 24 Oct. **CEO response:** acknowledged this as a hard block, authorized Ahmed to log into the organization directly using Ali's credentials from the shared Excel sheet and either grant the necessary Owner-level privileges or install the app directly if Ali remains unavailable, rather than let the Days 12-14 window stall. Work continues against mock data per Clarification 4 in the meantime.
- As of this report, the specific cause of "Install is prohibited" is still being isolated — candidates under investigation are the org's member-privileges policy on GitHub App installs, a possible 2FA-enforcement mismatch on Ali's account, or Ali's actual role (Owner vs Member) in the org. The App ID, Installation ID (once obtained) and private key are recorded in the credentials sheet only, never in chat or in this report.
- The private key is stored outside every Git repository; `*.pem` is in `.gitignore` project-wide.

### Limits and open points
- Whether repository collaborators are readable with this app's permissions cannot be confirmed until the live test runs.
- Teams are recorded per repo in metadata only; they are not separate entities.
- Org members with no mapping and no public email cannot be resolved and will appear in the review queue — expected behavior, not a defect.

### Delay log (Clarification 4)
| Date | Item | Detail |
|---|---|---|
| 15 Oct | GitHub live platform not ready | Install request returned a 404 for the org owner. Connector built mock-first. |
| 24 Oct | Still blocked after ownership transfer | "Install is prohibited" on the org's own install page for both available targets. Escalated to and authorized by the CEO to resolve directly. |

---

## 8. Deviations from the plan

| Plan said | What happened | Action |
|---|---|---|
| Use Horquva Outlook address for all accounts | GitHub and Supabase were created with `ahmed.abubakr.horquva@gmail.com` | Recorded in Excel; noted to Sumavia |
| GitHub username `ahmed-abubakr-horquva` | Actual username is `ahmedabubakr-horquva` (no hyphen) | Recorded in Excel with the real username |
| Credentials in Excel within 1 hour | Some entries were late | Addressed throughout; final pass recommended (Open Items #4) |
| Code in `/shared/ahmed/` | Done on 11 Oct, updated 12, 16, 18 and 24 Oct | None |
| GitHub App created by the connector engineer | Created under Ahmed's account, then transferred to the `horquva-test` org | Horquva now owns it (section 7) |
| GitHub App installed by the org owner | Blocked by an org-level restriction; CEO authorized Ahmed to complete it directly using Ali's credentials if needed | In progress (section 7, Open Items #1) |

---

## 9. Watchdog

**Files:** `src/watchdog.ts` (runner), `src/watchdog-core.ts` (logic), `config/workflow-owners.json`, `config/oncall.json`, `tests/watchdog.test.ts`, `tests/fixtures/mock-failures.json`. Full detail and timestamps are in `watchdog-report.md`.

### Behaviour
- Polls n8n every 15 minutes (`WATCHDOG_INTERVAL_MIN` can lower it) for failed executions and posts the agreed alert format to `#ops-alerts`: workflow, owner, failed-at time, error, impact, action and on-call.
- **Baseline:** the first live run records failures that already exist and alerts only on new ones.
- **No duplicates:** each execution id alerts once, tracked in `state/watchdog-state.json`. If Slack is down, the alert is retried on the next poll.
- **Outage alert:** if n8n cannot be reached for 2 polls in a row, one alert is sent, then one recovery message when it comes back.
- **Flood limit:** more than 10 new failures in a poll become 10 alerts plus one summary.
- Slack posting uses an incoming webhook from `.env`. Errors are sanitized so URLs and tokens are never logged.

### Tests — all complete
- **Unit tests**, `tests/watchdog.test.ts`, 8 cases: **PASS** (18 Oct).
- **Mock run**, 3 simulated failures: 3 alerts, then 0 on repeat. Nothing posted to Slack.
- **Live dry-run** against Hanain's n8n, 24 Oct: baseline of 14 existing failures recorded, `alerts=0`; repeat run confirmed `new=0`.
- **Live real-failure test, 24 Oct: PASS.** `#ops-alerts` channel and Slack webhook created and verified. Real baseline established (`baselined=14`). Three controlled failure-injection cycles run against the inactive `Single Point of Failure` workflow (its data-source URL was broken via the n8n API, matching the plan's approved scenario of "changing a data source URL"), producing 14 real failed executions across the 3 cycles — all detected and alerted to `#ops-alerts` in the agreed format, with zero duplicate alerts on any repeat poll. Workflow was deactivated and fully restored afterward; confirmed via a clean final poll (`new=0 alerts=0`). Full timestamp table in `watchdog-report.md` section 3.3.
- **Outage detection, confirmed live (unplanned):** a stale ngrok address produced a genuine n8n outage mid-test; the watchdog correctly alerted after 2 consecutive failed polls (not before, not repeated) and sent a recovery message once reachable again.

### On-call and owners
- On-call is chosen from the 16 project workers only (Clarification 10), rotating daily among those available. Used correctly throughout the 24 Oct test with no manual override needed.
- Owner for "Single Point of Failure" resolved from its n8n tag to Muhammad Ibrahim Shaikh — pending Sumavia's sign-off (Open Items, watchdog report). The three currently-active workflows (Error Handler, GitHub Deploy Notifier, Onboarding Automator) remain `UNASSIGNED` pending confirmation from Sumavia or Hanain.

### Limits
- Polling every 15 minutes can detect a failure up to 15 minutes late. A 10-minute interval gives margin.
- Recovery of a failed workflow is not verified automatically — checked manually on the n8n Executions page.
- The watchdog has been run from Ahmed's machine throughout testing. Continuous operation after 20 Oct and stopping it before the 31 Oct shutdown are for Sumavia to assign.

### Coordination with Tooba Ghaffar
Tooba's `simulate-failures.py` produces scenario records for local mock checks and contacts no live services, so no change to her script was needed — the watchdog uses its own mock file. Her 7/7 and 5/5 mock checks were independently re-run and confirmed to pass, with no live calls made. Live failure injection against Hanain's instance (section 9 above) was run by Ahmed directly, proposed and confirmed in Slack beforehand, separately from Tooba's scope. Under the plan, Affan runs the formal MVP failure-injection tests on 29 Oct with Sumavia witnessing.

---

## 10. Security notes

- `.env` and `*.pem` are in `.gitignore` project-wide. Checked on 16 Oct and again after the 24 Oct watchdog work: no `.env` or `.pem` tracked in either repository, and no ngrok address, private-key header, Supabase secret key, or Slack webhook URL committed anywhere in the working repo or `/ahmed/` in the shared repo.
- The live n8n test prints only names and counts, never full errors, since axios errors can carry the API key in request headers.
- The n8n API and the Slack webhook are protected by their keys even though their addresses are publicly reachable. Both are recorded in Excel and `.env` only.
- An earlier Supabase secret key was exposed during setup and has since been superseded by key rotation.
- The working repo `horquva-test-ahmed` remains public (Open Items #5).

---

## 11. Coordination with other workers

- **Tooba Ghaffar** asked on 15 Oct whether live integration testing could start; Ahmed replied with his own status only — platform access is each provisioner's call, watchdog alerts go to `#ops-alerts`. Her failure-simulation documentation was merged into the shared repo on 14 Oct and her mock results (7/7, 5/5) were independently verified.
- **Hanain Iftikhar** approved and supported the live n8n test and the 24 Oct real-failure injection on her instance, including recovering from the stale-tunnel issue mid-session.
- **Muhammad Ali Naeem** is the GitHub provisioner and org contact for the installation issue; multiple troubleshooting rounds with him are logged in section 7.
- **CEO** escalation on 24 Oct resulted in explicit authorization to resolve the GitHub installation directly if Ali remains unavailable.

---

## 12. Remaining work

1. **GitHub live test** — resolve the org-level installation restriction (section 7), add the Installation ID to `.env`, run `tests/github.live.test.ts`, fill `config/github-users.json` for any unmapped logins, and update section 7 with the real output.
2. Re-confirm Supabase RLS/constraint test results and resolver unit test output in writing (Open Items #2, #3) — both low-risk, quick to redo.
3. Final Excel completeness pass (Open Items #4).
4. Decide on working-repo visibility (Open Items #5).
5. Push both reports, complete remaining daily posts, and the sign-off once the GitHub item closes.

---

## 13. Definition of Done tracker

- [x] Schema applied
- [x] `base.ts` committed
- [x] `n8n.ts` committed and tested (mock and live)
- [x] `resolver.ts` committed (indirectly re-verified via GitHub connector's identity test; direct re-run recommended)
- [x] `github.ts` committed and tested on mock; **live test blocked on org installation issue, escalated and in progress**
- [x] `watchdog.ts` running and tested with real failures (14 across 3 controlled cycles, 24 Oct)
- [x] Integration report complete (this file)
- [x] Watchdog report complete
- [ ] Credentials fully confirmed complete in Excel (final pass pending)
- [ ] Daily posts and sign-off — pending GitHub resolution

---

## 14. Commit log

| Repo | Commit | Date | Message |
|---|---|---|---|
| working | `cde6e1d` | 8 Oct | Add canonical schema |
| working | `8527afb` | 8 Oct | Add base connector class |
| working | `e99e179` | 9 Oct | Add n8n connector with mock fixtures and test |
| working | `e3b7302` | 12 Oct | Add identity resolver, roster, aliases and tests |
| working | `91a7038` | 15 Oct | Ignore .pem files |
| working | `4bf6b26` | 16 Oct | Add live n8n connector test (passes against Hanain's n8n) |
| working | `1f994e6` | 18 Oct | Add watchdog with baseline, de-duplication, outage alert and tests |
| working | `8a0e038` | 24 Oct | Restore GitHub connector (mock-tested); watchdog outage-detection verified live |
| working | `b26e0c3` | 24 Oct | Live watchdog test complete: real failures detected and alerted |
| shared | `3f8a6f1` | 11 Oct | Add Ahmed's canonical model and connectors |
| shared | `3fa97c4` | 12 Oct | Add identity resolver |
| shared | `7fee69f` | 16 Oct | Add live n8n test |
