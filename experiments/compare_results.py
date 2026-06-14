from __future__ import annotations


def compare(secure_metrics: dict, baseline_metrics: dict) -> dict:
    return {
        "security_gain": secure_metrics.get("malicious_block_rate", 0) - baseline_metrics.get("malicious_block_rate", 0),
        "functionality_delta": secure_metrics.get("legitimate_success_rate", 0) - baseline_metrics.get("legitimate_success_rate", 0),
    }
