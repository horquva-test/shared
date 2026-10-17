
import json
from datetime import datetime, timezone


def simulate_failures():
    """Test five synthetic failures using local mock state only."""

    scenarios = [
        {
            "failure_id": "FAIL-001",
            "failure_type": "credential_unavailable",
            "mock_component": "n8n",
            "mock_state": {"credential_available": False},
            "trigger": "Required workflow credential is missing",
            "expected_detection": "Credential availability check fails",
            "recovery": "Restore an authorized test credential",
        },
        {
            "failure_id": "FAIL-002",
            "failure_type": "source_url_changed",
            "mock_component": "data_source",
            "mock_state": {
                "configured_url": "https://mock.example/changed",
                "expected_url": "https://mock.example/approved",
            },
            "trigger": "Configured source URL differs from expected test URL",
            "expected_detection": "Source URL validation reports a mismatch",
            "recovery": "Verify and restore the approved test URL",
        },
        {
            "failure_id": "FAIL-003",
            "failure_type": "notification_channel_missing",
            "mock_component": "Slack",
            "mock_state": {"channel_exists": False},
            "trigger": "Mock notification channel cannot be found",
            "expected_detection": "Notification delivery is marked unavailable",
            "recovery": "Select a valid mock/test notification destination",
        },
        {
            "failure_id": "FAIL-004",
            "failure_type": "model_provider_unavailable",
            "mock_component": "AI provider",
            "mock_state": {"provider_available": False},
            "trigger": "Mock AI provider is unavailable",
            "expected_detection": "Provider health check fails",
            "recovery": "Use an approved fallback or retry after recovery",
        },
        {
            "failure_id": "FAIL-005",
            "failure_type": "rate_limit_exceeded",
            "mock_component": "AI provider",
            "mock_state": {"http_status": 429},
            "trigger": "Mock provider returns a rate-limit response",
            "expected_detection": "Rate-limit response is recognized",
            "recovery": "Apply backoff and retry within the allowed limit",
        },
    ]

    def detect_failure(scenario):
        """Evaluate synthetic state; never call an external service."""
        failure_type = scenario["failure_type"]
        state = scenario["mock_state"]

        if failure_type == "credential_unavailable":
            return not state["credential_available"]

        if failure_type == "source_url_changed":
            return state["configured_url"] != state["expected_url"]

        if failure_type == "notification_channel_missing":
            return not state["channel_exists"]

        if failure_type == "model_provider_unavailable":
            return not state["provider_available"]

        if failure_type == "rate_limit_exceeded":
            return state["http_status"] == 429

        raise ValueError(f"Unknown failure type: {failure_type}")

    results = []

    for scenario in scenarios:
        detected = detect_failure(scenario)
        recovery_defined = bool(scenario["recovery"].strip())

        result = {
            **scenario,
            "mock_detection_result": detected,
            "recovery_action_defined": recovery_defined,
            "status": (
                "MOCK_CHECK_PASS"
                if detected and recovery_defined
                else "MOCK_CHECK_FAIL"
            ),
            "mode": "mock_only",
            "live_service_contacted": False,
        }

        # Automated checks for each scenario.
        assert detected, f"{scenario['failure_id']}: failure not detected"
        assert recovery_defined, (
            f"{scenario['failure_id']}: recovery action missing"
        )
        results.append(result)

    # Overall checks.
    assert len(results) == 5, "Expected exactly five scenarios"
    assert len({r["failure_id"] for r in results}) == 5, (
        "Failure IDs must be unique"
    )
    assert all(r["status"] == "MOCK_CHECK_PASS" for r in results)
    assert all(not r["live_service_contacted"] for r in results)

    return results


def main():
    results = simulate_failures()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "mock_only",
        "live_services_contacted": False,
        "live_services_changed": False,
        "total_scenarios": len(results),
        "mock_checks_passed": sum(
            r["status"] == "MOCK_CHECK_PASS" for r in results
        ),
        "mock_checks_failed": sum(
            r["status"] == "MOCK_CHECK_FAIL" for r in results
        ),
        "results": results,
    }

    print(json.dumps(report, indent=2))
    print("\nSummary:")
    print(f"Scenarios checked: {len(results)}")
    print(f"Mock checks passed: {report['mock_checks_passed']}")
    print(f"Mock checks failed: {report['mock_checks_failed']}")
    print("Mode: mock only")
    print("Live services contacted: no")
    print("Live services changed: no")


if __name__ == "__main__":
    main()