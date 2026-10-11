import json
from datetime import datetime, timezone


def simulate_failures():
    """Run mock-only failure scenarios without contacting live services."""

    scenarios = [
        {
            "failure_id": "FAIL-001",
            "failure_type": "credential_unavailable",
            "mock_component": "n8n",
            "trigger": "Required workflow credential is missing",
            "expected_detection": "Credential availability check fails",
            "recovery": "Restore an authorized test credential",
        },
        {
            "failure_id": "FAIL-002",
            "failure_type": "source_url_changed",
            "mock_component": "data_source",
            "trigger": "Configured source URL differs from expected test URL",
            "expected_detection": "Source URL validation reports a mismatch",
            "recovery": "Verify and restore the approved test URL",
        },
        {
            "failure_id": "FAIL-003",
            "failure_type": "notification_channel_missing",
            "mock_component": "Slack",
            "trigger": "Mock notification channel cannot be found",
            "expected_detection": "Notification delivery is marked unavailable",
            "recovery": "Select a valid mock/test notification destination",
        },
        {
            "failure_id": "FAIL-004",
            "failure_type": "model_provider_unavailable",
            "mock_component": "AI provider",
            "trigger": "Mock AI provider returns an unavailable response",
            "expected_detection": "Provider health check fails",
            "recovery": "Use an approved fallback or retry after recovery",
        },
        {
            "failure_id": "FAIL-005",
            "failure_type": "rate_limit_exceeded",
            "mock_component": "AI provider",
            "trigger": "Mock provider returns a rate-limit response",
            "expected_detection": "Rate-limit response is recognized",
            "recovery": "Apply backoff and retry within the allowed limit",
        },
    ]

    results = []

    for scenario in scenarios:
        result = {
            **scenario,
            "mode": "mock_only",
            "status": "SIMULATED",
            "live_service_contacted": False,
        }
        results.append(result)

    return results


def main():
    results = simulate_failures()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "mock_only",
        "live_services_changed": False,
        "total_scenarios": len(results),
        "results": results,
    }

    print(json.dumps(report, indent=2))
    print("\nSummary:")
    print(f"Scenarios simulated: {len(results)}")
    print("Mode: mock only")
    print("Live services contacted: no")
    print("Live services changed: no")


if __name__ == "__main__":
    main()
