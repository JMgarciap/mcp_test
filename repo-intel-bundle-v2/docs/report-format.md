# Report Format

The analysis produces two main outputs per repository:

1.  **JSON Data**: Complete structured data including raw signals, scores, and metadata.
2.  **Markdown Report**: A human-readable summary designed for quick consumption.

## Markdown Sections

### Executive Summary
A table displaying the three key scores:
-   **Quality**: General code hygiene and standards.
-   **Cloud Readiness**: Preparedness for cloud deployment (Docker, IaC).
-   **Risk**: Potential security or maintenance risks.

### Key Findings
A list of high-priority observations, such as:
-   Security vulnerabilities (secrets).
-   Critical missing components (CI, Tests).

### Detailed Signals
Breakdown of specific checks:
-   **Hygiene**: README, Manifests.
-   **CI/CD**: Providers detected.
-   **Testing**: Test files or directories.
-   **Infrastructure**: Docker, Terraform, Kubernetes.
-   **Security**: Secret patterns.
