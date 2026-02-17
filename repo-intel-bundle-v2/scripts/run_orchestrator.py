import os
import sys
import argparse
import logging
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback or allow running without dotenv if env vars are set otherwise
    pass

# Ensure we can import from src/orchestrator
sys.path.append(os.getcwd())

try:
    from dotenv import load_dotenv
    from orchestrator.pipeline import AssessmentPipeline
except ImportError as e:
    print("\n❌ Missing Dependencies!")
    print(f"Error: {e}")
    print("Please ensure you have installed the project dependencies:")
    print("  1. Create venv: python3 -m venv .venv")
    print("  2. Acivate venv: source .venv/bin/activate")
    print("  3. Install deps: pip install -e \".[ui]\"\n")
    print("Alternatively, run using the venv python directly:")
    print("  .venv/bin/python scripts/run_orchestrator.py ...\n")
    sys.exit(1)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OrchestratorCLI")

def main():
    parser = argparse.ArgumentParser(description="Run the AI Governance Orchestrator Pipeline")
    parser.add_argument("--project", type=str, required=True, help="Project Name (e.g., 'demo-audit')")
    parser.add_argument("--repos", type=str, nargs='+', required=True, help="List of Repo URLs to analyze")
    parser.add_argument("--ref", type=str, default="main", help="Git reference (default: main)")
    parser.add_argument("--workflow", type=str, help="Path to workflow.md file")
    
    args = parser.parse_args()
    
    # Load Environment
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("❌ GITHUB_TOKEN not found in .env variable.")
        sys.exit(1)
        
    logger.info(f"🚀 Starting Orchestrator for project: {args.project}")
    logger.info(f"🎯 Targets: {args.repos}")
    
    try:
        pipeline = AssessmentPipeline(
            github_token=token,
            api_base=os.getenv("GITHUB_API_URL"),
            output_dir="outputs"
        )
        
        if args.workflow:
            from orchestrator.workflow import WorkflowParser
            logger.info(f"📜 Executing Workflow: {args.workflow}")
            steps = WorkflowParser.parse_markdown(args.workflow)
            summary = pipeline.run_workflow(
                project_name=args.project,
                repo_urls=args.repos,
                workflow_steps=steps
            )
        else:
            summary = pipeline.run_project_assessment(
                project_name=args.project,
                repo_urls=args.repos,
                ref=args.ref,
                run_agents=not args.no_agents
            )
        
        logger.info("✅ Assessment Complete!")
        if "governance_report_path" in summary:
            logger.info(f"📄 Report: {summary['governance_report_path']}")
            
    except Exception as e:
        logger.error(f"❌ Execution Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
