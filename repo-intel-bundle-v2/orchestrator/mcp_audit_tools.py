import os
import json
import logging
import glob
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from orchestrator.tool_registry import registry
from orchestrator.pipeline import AssessmentPipeline
from orchestrator.workflow import WorkflowParser

logger = logging.getLogger(__name__)

# --- Helper Functions ---
def _get_pipeline():
    # Helper to get a configured pipeline instance
    github_token = os.getenv("GITHUB_TOKEN", "")
    return AssessmentPipeline(
        github_token=github_token,
        api_base=os.getenv("GITHUB_API_URL"),
        output_dir="outputs"
    )

def _get_project_path(project_name: str) -> str:
    return os.path.join("outputs", project_name)

# --- MCP Tools ---

@registry.register(
    name="audit.run",
    description="Run the orchestrator for a given project, repo list, and workflow."
)
def audit_run(project_name: str, repos: Any, workflow_path: str):
    """
    Runs the audit pipeline.
    
    Args:
        project_name: Name of the project (folder in outputs/).
        repos: List of strings or single string URL of repositories to audit.
        workflow_path: Path to the .md workflow file (e.g. 'examples/custom_workflow.md').
    """
    if isinstance(repos, str):
        repos = [repos]
        
    if not os.path.exists(workflow_path):
        return json.dumps({
            "status": "failed",
            "error": f"Workflow file not found: {workflow_path}"
        })

    try:
        pipeline = _get_pipeline()
        steps = WorkflowParser.parse_markdown(workflow_path)
        
        if not steps:
             return json.dumps({
                "status": "failed",
                "error": "No enabled phases found in workflow."
            })

        summary = pipeline.run_workflow(
            project_name=project_name,
            repo_urls=repos,
            workflow_steps=steps
        )
        
        # Extract key info for the return
        artifacts = []
        if "governance_report_path" in summary:
            artifacts.append(summary["governance_report_path"])
        if "seller_page_path" in summary:
            artifacts.append(summary["seller_page_path"])
            
        return json.dumps({
            "status": "success",
            "project_dir": f"outputs/{project_name}",
            "repos_analyzed": summary.get("repos_analyzed", []),
            "artifacts_created": artifacts,
            "next_actions": ["Run audit.index", "Run audit.context_pack"]
        }, indent=2)

    except Exception as e:
        logger.error(f"Audit run failed: {e}")
        return json.dumps({
            "status": "failed",
            "error": str(e)
        }, indent=2)

@registry.register(
    name="audit.index",
    description="Generate INDEX.md and COPILOT_BRIEF.md for a project."
)
def audit_index(project_name: str):
    project_dir = _get_project_path(project_name)
    if not os.path.exists(project_dir):
         return f"Error: Project directory '{project_dir}' not found. Run audit.run first."

    # Map Artifacts
    artifact_map = {
        "reports": glob.glob(os.path.join(project_dir, "*.md")),
        "data": glob.glob(os.path.join(project_dir, "*.json*")),
        "repos": glob.glob(os.path.join(project_dir, "repos", "*.md")),
        "agents": glob.glob(os.path.join(project_dir, "agents", "*.md")),
        "delivery": glob.glob(os.path.join(project_dir, "delivery", "*.md")),
        "confluence": glob.glob(os.path.join(project_dir, "confluence", "*.md")),
    }
    
    # Generate INDEX.md
    index_content = f"# Scan Index: {project_name}\n\n"
    index_content += "## 🗺️ Artifact Map\n"
    
    for category, paths in artifact_map.items():
        if paths:
            index_content += f"### {category.upper()}\n"
            for p in sorted(paths):
                index_content += f"- [{os.path.basename(p)}]({p})\n"
    
    index_path = os.path.join(project_dir, "INDEX.md")
    with open(index_path, "w") as f:
        f.write(index_content)
        
    # Generate COPILOT_BRIEF.md
    brief_content = f"""# Copilot Brief: {project_name}

## 🤖 Instructions for Copilot
You are analyzing the outputs of an automated audit run.
Use the artifacts listed in `INDEX.md` as your evidence base.

## 🔍 Key Evidence Sources
- **Governance**: Check `governance_summary.md` for overall score and compliance gaps.
- **Security**: Check `agents/*.vuln_detective.md` for specific vulnerabilities.
- **Delivery**: Check `delivery/roadmap.md` and `backlog.md` for agile planning status.
- **Code Quality**: Check `repos/*.md` for static analysis stats.

## 📝 Output Requirements
When asked to write a report:
1. Cite specific files as evidence.
2. Prioritize "Critical" and "High" severity issues.
3. Use the structure provided in `confluence/seller_page.md` as a baseline.
"""
    brief_path = os.path.join(project_dir, "COPILOT_BRIEF.md")
    with open(brief_path, "w") as f:
        f.write(brief_content)

    return json.dumps({
        "status": "success",
        "index_path": index_path,
        "brief_path": brief_path,
        "artifact_counts": {k: len(v) for k, v in artifact_map.items()}
    }, indent=2)

@registry.register(
    name="audit.context_pack",
    description="Generate a token-safe context pack string for the LLM."
)
def audit_context_pack(project_name: str, workflow_path: Optional[str] = None, max_chars: int = 20000):
    project_dir = _get_project_path(project_name)
    if not os.path.exists(project_dir):
         return f"Error: Project directory '{project_dir}' not found."

    context_buffer = []
    
    # 1. Header
    context_buffer.append(f"Project: {project_name}")
    context_buffer.append("---")
    
    # 2. Key Artifacts to Include (Priority Order)
    # We try to read them if they exist
    priority_files = [
        os.path.join(project_dir, "COPILOT_BRIEF.md"),
        os.path.join(project_dir, "governance_summary.md"),
        os.path.join(project_dir, "confluence", "seller_page.md"),
    ]
    
    # Add Delivery docs if exist
    priority_files.extend(glob.glob(os.path.join(project_dir, "delivery", "*.md")))
    
    # Add top 2 Repo docs
    priority_files.extend(glob.glob(os.path.join(project_dir, "repos", "*.md"))[:2])

    current_chars = 0
    included_files = []
    
    for fpath in priority_files:
        if os.path.exists(fpath):
            try:
                with open(fpath, "r") as f:
                    content = f.read()
                    
                # Simple truncation strategy: 
                # If adding this file exceeds max_chars, add truncated version or skip
                if current_chars + len(content) > max_chars:
                    remaining = max_chars - current_chars
                    if remaining > 50:
                        content = content[:remaining] + "\n... [TRUNCATED]"
                        context_buffer.append(f"\n\n=== FILE: {fpath} ===\n{content}")
                        included_files.append(fpath + " (partial)")
                        break # Stop adding
                    else:
                        continue # Skip to see if smaller files fit? Or just stop.
                else:
                    context_buffer.append(f"\n\n=== FILE: {fpath} ===\n{content}")
                    current_chars += len(content)
                    included_files.append(fpath)
            except Exception:
                pass

    return json.dumps({
        "context_pack_text": "\n".join(context_buffer),
        "included_artifacts": included_files,
        "total_chars": current_chars
    }, indent=2)

