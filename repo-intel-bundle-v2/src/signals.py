import re
from typing import List, Dict, Any

class SignalDetector:
    def __init__(self, file_paths: List[str], file_reader_callback):
        self.file_paths = file_paths
        self.read_file = file_reader_callback
        self.signals = {}

    def detect_all(self) -> Dict[str, Any]:
        self.signals.update(self._detect_hygiene())
        self.signals.update(self._detect_ci())
        self.signals.update(self._detect_tests())
        self.signals.update(self._detect_docker())
        self.signals.update(self._detect_dependencies())
        self.signals.update(self._detect_iac())
        self.signals.update(self._detect_secrets())
        return self.signals

    def _detect_hygiene(self) -> Dict[str, Any]:
        has_readme = any(f.lower().startswith("readme") for f in self.file_paths)
        # Manifest detection logic (simplified)
        manifests = [f for f in self.file_paths if f in ["package.json", "requirements.txt", "pom.xml", "build.gradle", "go.mod", "Cargo.toml"]]
        return {
            "has_readme": has_readme,
            "manifests_found": manifests,
            "has_manifest": len(manifests) > 0
        }

    def _detect_ci(self) -> Dict[str, Any]:
        has_github_actions = any(f.startswith(".github/workflows") and f.endswith(".yml") for f in self.file_paths)
        has_jenkins = any("jenkinsfile" in f.lower() for f in self.file_paths)
        has_gitlab_ci = ".gitlab-ci.yml" in self.file_paths
        has_circleci = ".circleci/config.yml" in self.file_paths
        has_travis = ".travis.yml" in self.file_paths
        
        return {
            "has_ci": has_github_actions or has_jenkins or has_gitlab_ci or has_circleci or has_travis,
            "ci_providers": [
                p for p, found in [
                    ("GitHub Actions", has_github_actions),
                    ("Jenkins", has_jenkins),
                    ("GitLab CI", has_gitlab_ci),
                    ("CircleCI", has_circleci),
                    ("Travis CI", has_travis)
                ] if found
            ]
        }

    def _detect_tests(self) -> Dict[str, Any]:
        # Simple heuristic: folder names or file patterns
        test_folders = ["tests", "test", "__tests__", "spec"]
        has_test_dirs = any(any(d in f.split("/") for d in test_folders) for f in self.file_paths)
        
        # Look for test files
        test_file_patterns = [r".*_test\.py$", r".*test_.*\.py$", r".*\.test\.js$", r".*\.spec\.js$", r".*Test\.java$"]
        has_test_files = False
        for f in self.file_paths:
            for pattern in test_file_patterns:
                if re.match(pattern, f):
                    has_test_files = True
                    break
            if has_test_files:
                break

        return {
            "has_tests": has_test_dirs or has_test_files
        }

    def _detect_docker(self) -> Dict[str, Any]:
        dockerfiles = [f for f in self.file_paths if "dockerfile" in f.lower()]
        
        issues = []
        has_docker = len(dockerfiles) > 0
        
        if has_docker:
            # Analyze the first Dockerfile found (simplification)
            content = self.read_file(dockerfiles[0])
            if content:
                if "USER root" in content:
                    issues.append("Runs as root user") # Can be a false positive if followed by USER nonroot, but good enough for now
                if ":latest" in content:
                    issues.append("Uses 'latest' tag")
                if "HEALTHCHECK" not in content:
                    issues.append("Missing HEALTHCHECK")
                if "curl | bash" in content or "wget -O -" in content: # heuristic
                    issues.append("Piping curl/wget to shell")

        return {
            "has_docker": has_docker,
            "dockerfile_issues": issues
        }

    def _detect_dependencies(self) -> Dict[str, Any]:
        lockfiles = ["package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock", "go.sum", "Cargo.lock"]
        has_lockfile = any(f in lockfiles for f in self.file_paths)
        return {
            "has_lockfile": has_lockfile
        }

    def _detect_iac(self) -> Dict[str, Any]:
        has_terraform = any(f.endswith(".tf") for f in self.file_paths)
        has_k8s = any(f.endswith(".yaml") or f.endswith(".yml") for f in self.file_paths) and any("apiVersion:" in self.read_file(f) for f in self.file_paths if (f.endswith(".yaml") or f.endswith(".yml")) and "github/workflows" not in f)
        has_helm = any("Chart.yaml" in f for f in self.file_paths)
        
        return {
            "has_iac": has_terraform or has_k8s or has_helm,
            "iac_providers": [
                p for p, found in [
                    ("Terraform", has_terraform),
                    ("Kubernetes", has_k8s),
                    ("Helm", has_helm)
                ] if found
            ]
        }

    def _detect_secrets(self) -> Dict[str, Any]:
        # Very simple regex for demonstrative purposes. 
        # CAUTION: High false positive rate.
        patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "Generic Private Key": r"-----BEGIN PRIVATE KEY-----",
            "GitHub Token": r"ghp_[a-zA-Z0-9]{36}"
        }
        
        found_secrets = []
        # Check only a subset of files to avoid performance hit, e.g., config files, slight extension
        # For simplicity, we check first 10 files that look like config or code
        checkable_extensions = (".py", ".js", ".json", ".yml", ".yaml", ".env", ".properties", ".xml")
        files_to_check = [f for f in self.file_paths if f.endswith(checkable_extensions)][:20] 

        for f in files_to_check:
            content = self.read_file(f)
            if not content: continue
            for name, pattern in patterns.items():
                if re.search(pattern, content):
                    found_secrets.append(f"{name} in {f}")

        return {
            "potential_secrets_found": found_secrets,
            "has_secrets_smell": len(found_secrets) > 0
        }
