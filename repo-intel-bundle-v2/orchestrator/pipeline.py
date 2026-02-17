import os
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import time

# Import Core Logic
from src.github_client import GitHubClient
from src.analyzer import RepoAnalyzer

# Import Agents Logic
from agents.vulnerability_agent import analyze_vulnerability, generate_report as run_vuln_report
from agents.test_coverage_agent import analyze_coverage, generate_report as run_test_report
from agents.integrator_agent import aggregate_data, generate_governance_report

# Import Seller Mode
from seller_mode.seller_formatter import SellerFormatter
from orchestrator.confluence_publisher import publish_to_confluence

from orchestrator.event_bus import EventBus
from agents.agile_planner_agent import run_agile_planner
from agents.execution_roadmap_agent import run_roadmap_generator
from agents.effort_estimator_agent import run_effort_estimator

# Import Workflow
from orchestrator.workflow import WorkflowEngine, WorkflowStep

logger = logging.getLogger(__name__)

class AssessmentPipeline:
    def __init__(self, github_token: str, api_base: Optional[str], output_dir: str):
        self.github_token = github_token
        self.api_base = api_base
        self.output_dir = output_dir
        
        # Internal state for context sharing between steps
        self.bus = None
        self.project_dir = None
        self.repos_dir = None
        self.agents_dir = None

    def _init_context(self, project_name: str, repo_urls: List[str]):
        """Initialize pipeline context and directories"""
        if not project_name:
            project_name = f"assessment_{int(time.time())}"
            
        self.bus = EventBus(self.output_dir, project_name)
        self.bus.emit("PROJECT", "STARTED", message=f"Starting assessment for {len(repo_urls)} repos", progress=0)
            
        self.project_dir = os.path.join(self.output_dir, project_name)
        self.repos_dir = os.path.join(self.project_dir, "repos")
        self.agents_dir = os.path.join(self.project_dir, "agents")
        
        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.agents_dir, exist_ok=True)
        
        return {
            "project_name": project_name,
            "project_dir": self.project_dir,
            "repos": repo_urls,
            "analyzed_slugs": [],
            "failures": []
        }

    # --- Modular Execution Steps ---

    def execute_repo_analysis(self, context: Dict[str, Any], **kwargs):
        """Phase: analysis"""
        self.bus.emit("MCP_ANALYZE", "STARTED", message="Initializing GitHub Client", progress=10, agent_id="mcp_analyze")
        client = GitHubClient(token=self.github_token, api_base_url=self.api_base)
        analyzer = RepoAnalyzer(client)
        
        for url in context["repos"]:
            repo_slug = url.split("/")[-1]
            try:
                self.bus.emit("MCP_ANALYZE", "IN_PROGRESS", repo=repo_slug, message=f"Analyzing {url}", agent_id="mcp_analyze")
                logger.info(f"Analyzing {url}...")
                
                # Use 'ref' from kwargs or default to None
                repo_result = analyzer.analyze(url, kwargs.get("ref"))
                
                slug = f"{repo_result['metadata']['owner']}_{repo_result['metadata']['repo']}"
                json_path = os.path.join(self.repos_dir, f"{slug}.json")
                md_path = os.path.join(self.repos_dir, f"{slug}.md")
                
                with open(json_path, "w") as f:
                    json.dump(repo_result, f, indent=2, default=str)
                with open(md_path, "w") as f:
                    f.write(repo_result.get("report_markdown", ""))
                
                self.bus.emit("MCP_ANALYZE", "COMPLETED", repo=slug, message="Analysis complete", artifact_paths=[json_path, md_path], agent_id="mcp_analyze")
                context["analyzed_slugs"].append(slug)
                
            except Exception as e:
                logger.error(f"Analysis failed for {url}: {e}")
                self.bus.emit("MCP_ANALYZE", "FAILED", repo=repo_slug, message=str(e), agent_id="mcp_analyze")
                context["failures"].append({"url": url, "stage": "analysis", "error": str(e)})

    def execute_security_scan(self, context: Dict[str, Any], **kwargs):
        """Phase: security"""
        for slug in context["analyzed_slugs"]:
            try:
                # Load Repo Data
                with open(os.path.join(self.repos_dir, f"{slug}.json")) as f:
                    repo_result = json.load(f)

                self.bus.emit("AGENT_SECURITY", "STARTED", repo=slug, message="Running Vulnerability Detective", agent_id="security")
                vuln_result = analyze_vulnerability(repo_result)
                vuln_json_path = os.path.join(self.agents_dir, f"{slug}.vuln_detective.json")
                vuln_md_path = os.path.join(self.agents_dir, f"{slug}.vuln_detective.md")
                
                with open(vuln_json_path, "w") as f:
                    json.dump(vuln_result, f, indent=2, default=str)
                with open(vuln_md_path, "w") as f:
                    f.write(run_vuln_report(vuln_result))
                
                self.bus.emit("AGENT_SECURITY", "COMPLETED", repo=slug, artifact_paths=[vuln_json_path, vuln_md_path], agent_id="security")
            except Exception as e:
                logger.error(f"Security scan failed for {slug}: {e}")
                context["failures"].append({"repo": slug, "stage": "security", "error": str(e)})

    def execute_test_coverage(self, context: Dict[str, Any], **kwargs):
        """Phase: tests"""
        for slug in context["analyzed_slugs"]:
            try:
                # Load Repo Data
                with open(os.path.join(self.repos_dir, f"{slug}.json")) as f:
                    repo_result = json.load(f)

                self.bus.emit("AGENT_TESTS", "STARTED", repo=slug, message="Running Test Coverage Agent", agent_id="tests")
                test_result = analyze_coverage(repo_result)
                test_json_path = os.path.join(self.agents_dir, f"{slug}.test_coverage.json")
                test_md_path = os.path.join(self.agents_dir, f"{slug}.test_coverage.md")
                
                with open(test_json_path, "w") as f:
                    json.dump(test_result, f, indent=2, default=str)
                with open(test_md_path, "w") as f:
                    f.write(run_test_report(test_result))
                
                self.bus.emit("AGENT_TESTS", "COMPLETED", repo=slug, artifact_paths=[test_json_path, test_md_path], agent_id="tests")
            except Exception as e:
                logger.error(f"Test coverage failed for {slug}: {e}")
                context["failures"].append({"repo": slug, "stage": "tests", "error": str(e)})

    def execute_governance_check(self, context: Dict[str, Any], **kwargs):
        """Phase: governance"""
        try:
            self.bus.emit("INTEGRATOR", "STARTED", message="Aggregating portfolio data", agent_id="integrator")
            portfolio = aggregate_data(self.project_dir)
            gov_report = generate_governance_report(portfolio, context["project_name"])
            
            gov_json_path = os.path.join(self.project_dir, "governance_summary.json")
            gov_md_path = os.path.join(self.project_dir, "governance_summary.md")
            
            with open(gov_json_path, "w") as f:
                json.dump(portfolio, f, indent=2, default=str)
            with open(gov_md_path, "w") as f:
                f.write(gov_report)
                
            context["governance_report_path"] = gov_md_path
            context["portfolio_data"] = portfolio # Cache for next steps
            self.bus.emit("INTEGRATOR", "COMPLETED", artifact_paths=[gov_json_path, gov_md_path], progress=70, agent_id="integrator")
        except Exception as e:
            logger.error(f"Governance check failed: {e}")
            context["failures"].append({"stage": "governance", "error": str(e)})

    def execute_delivery_planning(self, context: Dict[str, Any], **kwargs):
        """Phase: planning"""
        try:
            portfolio = context.get("portfolio_data")
            if not portfolio:
                # Re-aggregate if not in context (e.g. if governance step was skipped)
                portfolio = aggregate_data(self.project_dir)
            
            delivery_dir = os.path.join(self.project_dir, "delivery")
            os.makedirs(delivery_dir, exist_ok=True)
            
            # Agile Planner
            self.bus.emit("AGILE_PLANNER", "STARTED", message="Generating Backlog", agent_id="planner")
            backlog_md = run_agile_planner(portfolio, delivery_dir)
            backlog_path = os.path.join(delivery_dir, "backlog.md")
            with open(backlog_path, "w") as f: f.write(backlog_md)
            self.bus.emit("AGILE_PLANNER", "COMPLETED", artifact_paths=[backlog_path], agent_id="planner")
            
            # Execution Roadmap
            self.bus.emit("EXEC_ROADMAP", "STARTED", message="Creating Roadmap", agent_id="roadmap")
            roadmap_md = run_roadmap_generator(portfolio, delivery_dir)
            roadmap_path = os.path.join(delivery_dir, "roadmap.md")
            with open(roadmap_path, "w") as f: f.write(roadmap_md)
            self.bus.emit("EXEC_ROADMAP", "COMPLETED", artifact_paths=[roadmap_path], agent_id="roadmap")
            
            # Effort Estimator
            self.bus.emit("EFFORT_ESTIMATOR", "STARTED", message="Estimating Effort", agent_id="estimator")
            effort_md = run_effort_estimator(portfolio, delivery_dir)
            effort_path = os.path.join(delivery_dir, "effort_estimation.md")
            with open(effort_path, "w") as f: f.write(effort_md)
            self.bus.emit("EFFORT_ESTIMATOR", "COMPLETED", artifact_paths=[effort_path], progress=85, agent_id="estimator")
            
        except Exception as e:
            logger.error(f"Delivery planning failed: {e}")
            context["failures"].append({"stage": "planning", "error": str(e)})

    def execute_reporting(self, context: Dict[str, Any], **kwargs):
        """Phase: reporting"""
        try:
            portfolio = context.get("portfolio_data") or aggregate_data(self.project_dir)
            
            self.bus.emit("SELLER_MODE", "STARTED", message="Generating Executive Report", agent_id="seller")
            formatter = SellerFormatter(self.output_dir)
            seller_page_path = formatter.generate_seller_page(context["project_name"], portfolio)
            context["seller_page_path"] = seller_page_path
            
            self.bus.emit("SELLER_MODE", "COMPLETED", artifact_paths=[seller_page_path], progress=90, agent_id="seller")
            
            self.bus.emit("PUBLISH", "STARTED", message="Publishing to Confluence", agent_id="mcp_press")
            publish_to_confluence(seller_page_path)
            self.bus.emit("PUBLISH", "COMPLETED", progress=95, agent_id="mcp_press")
        except Exception as e:
            logger.error(f"Reporting failed: {e}")
            context["failures"].append({"stage": "reporting", "error": str(e)})


    # --- Unified Entry Points ---

    def run_workflow(self, project_name: str, repo_urls: List[str], workflow_steps: List[WorkflowStep]) -> Dict[str, Any]:
        """
        Runs a custom workflow consisting of defined steps.
        """
        context = self._init_context(project_name, repo_urls)
        engine = WorkflowEngine(self)
        
        # Add basic context shared across steps
        context["github_token"] = self.github_token
        
        engine.run_workflow(workflow_steps, context)
        
        self.bus.emit("PROJECT", "COMPLETED", progress=100, message="Workflow execution finished")
        return context

    def run_project_assessment(self, project_name: str, repo_urls: List[str], ref: Optional[str] = None, run_agents: bool = True) -> Dict[str, Any]:
        """
        Legacy entry point: constructs a standard workflow.
        """
        steps = [WorkflowStep(phase="analysis", params={"ref": ref})]
        
        if run_agents:
            steps.extend([
                WorkflowStep(phase="security"),
                WorkflowStep(phase="tests"),
                WorkflowStep(phase="governance"),
                WorkflowStep(phase="planning"),
                WorkflowStep(phase="reporting")
            ])
            
        return self.run_workflow(project_name, repo_urls, steps)
