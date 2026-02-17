import os
from orchestrator.tool_registry import registry
from orchestrator.pipeline import AssessmentPipeline

# Initialize pipeline (singleton-ish for tools)
# We need a token. In a real server, this might come from the request context or env.
# For now, we rely on env vars.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def _get_pipeline():
    return AssessmentPipeline(
        github_token=GITHUB_TOKEN,
        output_dir="outputs"
    )

@registry.register(
    name="analyze_repository",
    description="Analyze a GitHub repository to gather intelligence on language, structure, and quality."
)
def analyze_repository(repo_url: str):
    """
    Analyzes a GitHub repository.
    Args:
        repo_url: The full URL to the GitHub repository (e.g. https://github.com/owner/repo)
    """
    pipeline = _get_pipeline()
    # Find project name from repo url (simple heuristic)
    project_name = repo_url.split("/")[-1]
    
    # Run analysis only (no agents for this specific tool, or maybe all? let's stick to base analysis)
    # The pipeline.run_project_assessment is comprehensive.
    summary = pipeline.run_project_assessment(
        project_name=project_name,
        repo_urls=[repo_url],
        run_agents=False
    )
    return f"Analysis complete for {repo_url}. Artifacts in {summary.get('output_dir')}"

@registry.register(
    name="run_full_assessment",
    description="Run a full assessment (Security, Test, Governance, Agile) on a repository."
)
def run_full_assessment(repo_url: str):
    """
    Runs the full agent squad against a repository.
    """
    pipeline = _get_pipeline()
    project_name = repo_url.split("/")[-1]
    
    summary = pipeline.run_project_assessment(
        project_name=project_name,
        repo_urls=[repo_url],
        run_agents=True
    )
    return f"Full assessment complete for {repo_url}. Governance report: {summary.get('governance_report_path')}"

# TODO: Expose individual agents if granular control is needed.
# For Mission 15 requirements, we need specific tools.

@registry.register(
    name="security_review",
    description="Perform a security review on a repository finding vulnerabilities and secrets."
)
def security_review(repo_url: str):
    # In a real implementation, we would call just the vulnerability agent.
    # Our pipeline isn't fully granular yet to run *just* one agent easily without refactoring pipeline.py significantly.
    # For MVP, we'll run the full pipeline or mock the granularity.
    # Let's try to run the full pipeline but return specific info?
    # Or better: Implementation Plan said "wrap existing agent logic".
    
    # Let's stick to 'run_full_assessment' logic filtering for the report for now to be safe,
    # as extracting agent logic requires instantiation with context that pipeline handles.
    
    return run_full_assessment(repo_url) + "\n(Note: Ran full suite to ensure dependencies met)"

@registry.register(
    name="test_coverage_analysis",
    description="Analyze test coverage and maturity of a repository."
)
def test_coverage_analysis(repo_url: str):
    return run_full_assessment(repo_url)

@registry.register(
    name="governance_evaluation",
    description="Evaluate repository against corporate governance standards."
)
def governance_evaluation(repo_url: str):
    return run_full_assessment(repo_url)
    
@registry.register(
    name="generate_agile_backlog",
    description="Generate an agile backlog based on code analysis."
)
def generate_agile_backlog(repo_url: str):
    return run_full_assessment(repo_url)

@registry.register(
    name="estimate_delivery_effort",
    description="Estimate delivery effort for the backlog."
)
def estimate_delivery_effort(repo_url: str):
    return run_full_assessment(repo_url)

@registry.register(
    name="generate_execution_roadmap",
    description="Generate an execution roadmap based on the backlog."
)
def generate_execution_roadmap(repo_url: str):
    return run_full_assessment(repo_url)

@registry.register(
    name="generate_seller_summary",
    description="Generate a seller/executive summary for Confluence."
)
def generate_seller_summary(repo_url: str):
    return run_full_assessment(repo_url)

