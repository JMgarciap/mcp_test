from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import os
import json
import logging
from dotenv import load_dotenv

from orchestrator.pipeline import AssessmentPipeline
from src.utils import setup_logging

# Setup
load_dotenv()
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP for Orchestrator
mcp = FastMCP("repo-intel-orchestrator")

# Global Dependencies
github_token = os.getenv("GITHUB_TOKEN")
api_base = os.getenv("GITHUB_API_BASE_URL")
output_dir = os.getenv("OUTPUT_DIR", "outputs")

# Helper to check config
def _check_config():
    if not github_token:
        logger.warning("GITHUB_TOKEN is missing. Pipeline may fail.")
        return False
    return True

@mcp.tool()
def run_project_assessment(project_name: str, repo_urls: List[str], ref: Optional[str] = None, run_agents: bool = True) -> str:
    """
    Runs an end-to-end repository assessment pipeline.
    
    1. Analyzes specified repositories (Mission 1)
    2. Runs specialized agents (Mission 2)
    3. Generates governance reports (Mission 3)
    
    Args:
        project_name: Name of the project/assessment (creates a folder in outputs/).
        repo_urls: List of GitHub repository URLs to analyze.
        ref: Branch or tag to analyze (optional).
        run_agents: Whether to run post-processing agents (default: True).
    """
    if not _check_config():
         return json.dumps({"error": "Configuration missing (GITHUB_TOKEN). Check .env file."})

    try:
        pipeline = AssessmentPipeline(github_token, api_base, output_dir)
        result = pipeline.run_project_assessment(project_name, repo_urls, ref, run_agents)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run()
