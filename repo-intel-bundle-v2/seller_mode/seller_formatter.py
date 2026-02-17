import os
import json
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class SellerFormatter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def generate_seller_page(self, project_name: str, governance_data: list):
        """
        Generates the Confluence-ready Markdown page.
        """
        template = self.env.get_template("confluence_seller_page.md.tmpl")
        
        repos = governance_data.get("repos", [])
        
        # Calculate Metrics
        total_risk = sum([r['scores'].get('risk', 0) for r in repos])
        avg_risk = total_risk / len(repos) if repos else 0
        
        # Generate Tables
        scorecards = self._generate_scorecards(repos)
        
        # Extract Insights (Placeholder logic for now)
        quick_wins = ["Fix missing lockfiles (Low Effort, High Security Impact)"] if any(r.get('security_score', 0) < 95 for r in repos) else ["Maintain current security posture"]
        
        context = {
            "project_name": project_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "executive_summary": f"Assessment of {len(repos)} repositories. Overall portfolio risk is {'High' if avg_risk > 50 else 'Low'}.",
            "quick_wins": quick_wins,
            "portfolio_risk": f"{avg_risk:.1f}/100",
            "scorecards_table": scorecards,
            "roadmap_content": "### Phase 1: Immediate Remediation\n- Focus on repositories with Risk > 50.\n\n### Phase 2: Standardization\n- Enforce CI/CD across all projects.",
            "insights_content": "### Top Insight: Dependency Management\nMost repositories lack proper dependency locking mechanisms.",
            "appendix_content": f"See `governance_summary.md` for full technical details."
        }
        
        output_content = template.render(context)
        
        # Save
        confluence_dir = os.path.join(self.output_dir, project_name, "confluence")
        os.makedirs(confluence_dir, exist_ok=True)
        output_path = os.path.join(confluence_dir, "seller_page.md")
        
        with open(output_path, "w") as f:
            f.write(output_content)
            
        logger.info(f"Generated Seller Page at {output_path}")
        return output_path

    def _generate_scorecards(self, data):
        md = "| Repo | Quality | Risk | Security |\n|---|---|---|---|\n"
        for r in data:
            md += f"| {r['name']} | {r['scores']['quality']} | {r['scores']['risk']} | {r.get('security_score', 'N/A')} |\n"
        return md
