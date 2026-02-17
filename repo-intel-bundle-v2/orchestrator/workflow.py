import logging
import os
from typing import List, Dict, Any, Callable
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WorkflowStep(BaseModel):
    phase: str
    enabled: bool = True
    params: Dict[str, Any] = {}

class WorkflowParser:
    @staticmethod
    def parse_markdown(file_path: str) -> List[WorkflowStep]:
        """
        Parses a markdown file looking for checklist items:
        - [x] phase: security
        - [ ] phase: reporting (skipped)
        """
        steps = []
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow file not found: {file_path}")

        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("- ["):
                    enabled = line.startswith("- [x]")
                    content = line[5:].strip()
                    
                    # Parse phase:name key=value
                    parts = content.split(" ")
                    phase_part = parts[0]
                    
                    if phase_part.startswith("phase:"):
                        phase_name = phase_part.split(":")[1]
                        params = {}
                        for part in parts[1:]:
                            if "=" in part:
                                k, v = part.split("=")
                                params[k] = v
                        
                        if enabled:
                            steps.append(WorkflowStep(phase=phase_name, enabled=True, params=params))
                            
        return steps

class WorkflowEngine:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.phase_map: Dict[str, Callable] = {
            "analysis": self.pipeline.execute_repo_analysis,
            "security": self.pipeline.execute_security_scan,
            "tests": self.pipeline.execute_test_coverage,
            "governance": self.pipeline.execute_governance_check,
            "planning": self.pipeline.execute_delivery_planning,
            "reporting": self.pipeline.execute_reporting
        }

    def run_workflow(self, steps: List[WorkflowStep], context: Dict[str, Any]):
        logger.info(f"🚀 Starting Workflow Execution with {len(steps)} steps.")
        
        for step in steps:
            if step.phase in self.phase_map:
                logger.info(f"▶️ Executing Phase: {step.phase}")
                try:
                    # Execute the mapped method
                    self.phase_map[step.phase](context, **step.params)
                except Exception as e:
                    logger.error(f"❌ Phase {step.phase} failed: {e}")
                    # Decide if we stop or continue? For now, continue but mark error
                    context.setdefault("failures", []).append({"phase": step.phase, "error": str(e)})
            else:
                logger.warning(f"⚠️ Unknown phase: {step.phase}")
