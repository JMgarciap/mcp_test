from typing import Dict, Any

def calculate_scores(signals: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculates Quality, Cloud Readiness, and Risk scores (0-100).
    """
    
    # 1. Quality Score
    # Start: 50. Modifiers based on hygiene, tests, CI.
    quality = 50
    if signals.get("has_readme"): quality += 10
    if signals.get("has_manifest"): quality += 10
    if signals.get("has_ci"): quality += 15
    if signals.get("has_tests"): quality += 15
    if signals.get("has_lockfile"): quality += 10 # Reproducibility
    
    # Cap at 100
    quality = min(100, quality)


    # 2. Cloud Readiness Score
    # Start: 30. Boost for Docker, IaC, 12-factor traits (env vars - hard to detect statically reliably without deep analysis, so we use proxy signals).
    readiness = 30
    if signals.get("has_docker"): readiness += 30
    if signals.get("has_iac"): readiness += 20
    if signals.get("has_ci"): readiness += 10
    if signals.get("has_lockfile"): readiness += 10
    
    # Penalize if Dockerfile has issues
    docker_issues = signals.get("dockerfile_issues", [])
    readiness -= (len(docker_issues) * 5)

    readiness = max(0, min(100, readiness))


    # 3. Risk Score (Higher is WORSE)
    # Start: 10. Increase for secrets, missing tests, old dependencies (not impl), missing CI.
    risk = 10
    if signals.get("has_secrets_smell"): risk += 40
    if not signals.get("has_tests"): risk += 20
    if not signals.get("has_ci"): risk += 10
    
    docker_issues = signals.get("dockerfile_issues", [])
    if "Runs as root user" in docker_issues: risk += 10
    if "Uses 'latest' tag" in docker_issues: risk += 5

    risk = min(100, risk)

    return {
        "quality": quality,
        "cloud_readiness": readiness,
        "risk": risk
    }
