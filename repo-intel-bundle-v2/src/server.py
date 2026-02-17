from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Dict, Any
import os
import json
import logging
from dotenv import load_dotenv

from .utils import setup_logging, get_env_var
from .github_client import GitHubClient
from .analyzer import RepoAnalyzer

# Setup logic
load_dotenv()
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("repo-intel-bundle-v2")

# Global dependencies (lazy loaded or verified on startup)
github_token = os.getenv("GITHUB_TOKEN")
api_base = os.getenv("GITHUB_API_BASE_URL")
output_dir = os.getenv("OUTPUT_DIR", "outputs")

if not github_token:
    logger.warning("GITHUB_TOKEN not found in environment. Server may fail to fetch private repos or hit rate limits.")

@mcp.tool()
def analyze_repo(repo_url: str, ref: Optional[str] = None) -> str:
    """
    Analyzes a single GitHub repository and returns the JSON result.
    Does NOT write to file (use analyze_repos for that).
    
    Args:
        repo_url: Full URL of the repository (e.g., https://github.com/owner/repo)
        ref: Branch or commit hash (optional, defaults to repo default)
    """
    logger.info(f"Analyzing repo: {repo_url} @ {ref or 'default'}")
    
    if not github_token:
        return json.dumps({"error": "GITHUB_TOKEN is missing."})

    try:
        client = GitHubClient(token=github_token, api_base_url=api_base)
        analyzer = RepoAnalyzer(client)
        result = analyzer.analyze(repo_url, ref)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return json.dumps({"error": str(e)})

@mcp.tool()
def analyze_repos(repo_urls: List[str], ref: Optional[str] = None, project_name: Optional[str] = None) -> str:
    """
    Analyzes multiple repositories, writes outputs to local disk, and returns a summary.
    
    Args:
        repo_urls: List of repository URLs.
        ref: Branch/tag to use for all repos (optional).
        project_name: Name of the project fold to store outputs (default: timestamp).
    """
    import time
    
    if not github_token:
        return json.dumps({"error": "GITHUB_TOKEN is missing."})

    client = GitHubClient(token=github_token, api_base_url=api_base)
    analyzer = RepoAnalyzer(client)

    # Determine output folder
    if not project_name:
        project_name = f"analysis_{int(time.time())}"
    
    project_dir = os.path.join(output_dir, project_name)
    repos_dir = os.path.join(project_dir, "repos")
    
    os.makedirs(repos_dir, exist_ok=True)
    
    summary = {
        "project_name": project_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repos_analyzed": [],
        "failures": []
    }
    
    for url in repo_urls:
        try:
            logger.info(f"Processing {url}...")
            # 1. Analyze
            result = analyzer.analyze(url, ref)
            
            # 2. Write Individual Outputs
            owner = result["metadata"]["owner"]
            repo = result["metadata"]["repo"]
            safe_slug = f"{owner}_{repo}"
            
            json_path = os.path.join(repos_dir, f"{safe_slug}.json")
            md_path = os.path.join(repos_dir, f"{safe_slug}.md")
            
            with open(json_path, "w") as f:
                json.dump(result, f, indent=2, default=str)
                
            with open(md_path, "w") as f:
                f.write(result.get("report_markdown", ""))
                
            # 3. Add to Summary
            summary["repos_analyzed"].append({
                "repo": f"{owner}/{repo}",
                "url": url,
                "scores": result["scores"],
                "paths": {
                    "json": json_path,
                    "md": md_path
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            summary["failures"].append({
                "url": url,
                "error": str(e)
            })
            
    # Write Summary Files
    summary_json_path = os.path.join(project_dir, "summary.json")
    summary_md_path = os.path.join(project_dir, "summary.md")
    
    with open(summary_json_path, "w") as f:
        json.dump(summary, f, indent=2)
        
    # Generate Summary Markdown
    md_lines = [f"# Analysis Summary: {project_name}", ""]
    md_lines.append(f"**Date:** {summary['timestamp']}")
    md_lines.append(f"**Total Repos:** {len(repo_urls)}")
    md_lines.append(f"**Success:** {len(summary['repos_analyzed'])}")
    md_lines.append(f"**Failed:** {len(summary['failures'])}")
    md_lines.append("")
    
    md_lines.append("## Repository Scores")
    md_lines.append("| Repo | Quality | Cloud Readiness | Risk |")
    md_lines.append("| :--- | :--- | :--- | :--- |")
    
    for r in summary["repos_analyzed"]:
        s = r["scores"]
        md_lines.append(f"| {r['repo']} | {s['quality']} | {s['cloud_readiness']} | {s['risk']} |")
        
    if summary["failures"]:
        md_lines.append("")
        md_lines.append("## Failures")
        for f in summary["failures"]:
            md_lines.append(f"- **{f['url']}**: {f['error']}")
            
    with open(summary_md_path, "w") as f:
        f.write("\n".join(md_lines))

    return json.dumps(summary, indent=2)

def main():
    import sys
    # Adding a simple CLI wrapper for manual testing/make sample
    if "--sample" in sys.argv:
        # Check if sample file exists
        sample_file = "examples/repos_list.sample.json"
        if os.path.exists(sample_file):
            with open(sample_file) as f:
                 data = json.load(f)
                 print("Running sample analysis on:", data)
                 # Mock call
                 print(analyze_repos(data))
        else:
            print(f"Sample file {sample_file} not found.")
    else:
        mcp.run()

if __name__ == "__main__":
    main()
