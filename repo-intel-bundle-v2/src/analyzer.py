from datetime import datetime, timezone
import os
from typing import Optional, Dict, Any, List
from .github_client import GitHubClient
from .signals import SignalDetector
from .scoring import calculate_scores
from .report import ReportGenerator

class RepoAnalyzer:
    def __init__(self, github_client: GitHubClient):
        self.gh = github_client

    def analyze(self, repo_url: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates the analysis of a single repository.
        """
        owner, repo = self.gh.parse_repo_url(repo_url)
        
        # 1. Fetch Metadata
        metadata = self.gh.get_repo_metadata(owner, repo)
        default_branch = metadata.get("default_branch", "main")
        target_ref = ref or default_branch

        # 2. Fetch File Tree
        file_tree = self.gh.list_tree(owner, repo, target_ref)

        # 3. Detect Signals
        # Helper to read files on demand
        def file_reader(path: str) -> str:
            return self.gh.read_file(owner, repo, path, target_ref)

        detector = SignalDetector(file_tree, file_reader)
        signals = detector.detect_all()

        # 4. Calculate Scores
        scores = calculate_scores(signals)

        # 5. Generate Findings (Derived from signals/scores)
        findings = self._generate_findings(signals, scores)

        # 6. Construct Result Object
        result = {
            "repo_url": repo_url,
            "ref": target_ref,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "owner": owner,
                "repo": repo,
                "stars": metadata.get("stargazers_count", 0),
                "language": metadata.get("language")
            },
            "scores": scores,
            "signals": signals,
            "findings": findings
        }
        
        # 7. Generate Markdown Report
        reporter = ReportGenerator(result)
        result["report_markdown"] = reporter.to_markdown()

        return result

    def _generate_findings(self, signals: Dict[str, Any], scores: Dict[str, int]) -> List[Dict[str, Any]]:
        findings = []
        
        # Simple rule-based findings generation
        if signals.get("has_secrets_smell"):
            findings.append({
                "id": "SEC-001",
                "category": "Security",
                "severity": "High",
                "title": "Potential Secrets Detected",
                "description": "Found patterns resembling secrets (keys, tokens) in the codebase.",
                "evidence": signals.get("potential_secrets_found", [])
            })

        if not signals.get("has_ci"):
             findings.append({
                "id": "OPS-001",
                "category": "Operations",
                "severity": "Medium",
                "title": "Missing CI/CD Pipeline",
                "description": "No CI configuration files (GitHub Actions, Jenkins, etc.) were detected.",
                "evidence": []
            })
            
        if not signals.get("has_tests"):
             findings.append({
                "id": "QUAL-001",
                "category": "Quality",
                "severity": "Medium",
                "title": "Missing Tests",
                "description": "No test directories or test files were detected.",
                "evidence": []
            })

        if signals.get("dockerfile_issues"):
             findings.append({
                "id": "CONTAINER-001",
                "category": "Cloud",
                "severity": "Low",
                "title": "Dockerfile Best Practices",
                "description": "Issues found in Dockerfile.",
                "evidence": signals.get("dockerfile_issues", [])
            })
            
        return findings
