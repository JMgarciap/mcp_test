import os
import json
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self, output_dir: str, project_name: str):
        self.output_dir = output_dir
        self.project_name = project_name
        
        self.project_dir = os.path.join(output_dir, project_name)
        self.events_path = os.path.join(self.project_dir, "events.jsonl")
        self.status_path = os.path.join(self.project_dir, "status.json")
        
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Initialize status structure
        self.status_data = {
            "project": project_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "overall": {"progress": 0, "status": "PENDING"},
            "stages": {
                "MCP_ANALYZE": {"status": "PENDING", "progress": 0},
                "AGENT_SECURITY": {"status": "PENDING", "progress": 0},
                "AGENT_TESTS": {"status": "PENDING", "progress": 0},
                "INTEGRATOR": {"status": "PENDING", "progress": 0},
                "AGILE_PLANNER": {"status": "PENDING", "progress": 0},
                "EXEC_ROADMAP": {"status": "PENDING", "progress": 0},
                "EFFORT_ESTIMATOR": {"status": "PENDING", "progress": 0},
                "SELLER_MODE": {"status": "PENDING", "progress": 0},
                "PUBLISH": {"status": "PENDING", "progress": 0}
            },
            "repos": {}
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()

    def emit(self, stage: str, status: str, repo: Optional[str] = None, message: str = "", progress: int = 0, artifact_paths: Optional[List[str]] = None, agent_id: Optional[str] = None):
        """
        Emits an event to jsonl and updates the status json.
        """
        try:
            ts = datetime.utcnow().isoformat()
            
            event = {
                "ts": ts,
                "project": self.project_name,
                "repo": repo,
                "stage": stage,
                "status": status,
                "progress": progress,
                "message": message,
                "artifact_paths": artifact_paths or [],
                "meta": {"agent_id": agent_id} if agent_id else {}
            }
            
            # Write to JSONL
            with self.lock:
                with open(self.events_path, "a") as f:
                    f.write(json.dumps(event) + "\n")
                
                # Update snapshot
                self._update_status_snapshot(event)
                
        except Exception as e:
            logger.error(f"EventBus error: {e}", exc_info=True)
            # Best effort: Swallow error to avoid crashing pipeline

    def _update_status_snapshot(self, event):
        """Updates internal status dict and writes to status.json"""
        try:
            self.status_data["updated_at"] = event["ts"]
            
            stage = event["stage"]
            repo = event["repo"]
            status = event["status"]
            
            # Update Repo Status
            if repo:
                if repo not in self.status_data["repos"]:
                    self.status_data["repos"][repo] = {
                        "overall": {"status": "PENDING"},
                        "stages": {},
                        "artifacts": []
                    }
                
                self.status_data["repos"][repo]["stages"][stage] = status
                if event["artifact_paths"]:
                    self.status_data["repos"][repo]["artifacts"].extend(event["artifact_paths"])
                    # Deduplicate
                    self.status_data["repos"][repo]["artifacts"] = list(set(self.status_data["repos"][repo]["artifacts"]))

            # Update Project Stage Status (Simple aggregation or direct mapping)
            if stage in self.status_data["stages"]:
                self.status_data["stages"][stage]["status"] = status
                self.status_data["stages"][stage]["progress"] = event["progress"]

            # Update Overall Project Status
            if stage == "PROJECT":
                self.status_data["overall"]["status"] = status
                self.status_data["overall"]["progress"] = event["progress"]
            
            # Write status.json
            with open(self.status_path, "w") as f:
                json.dump(self.status_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Status Snapshot error: {e}")
