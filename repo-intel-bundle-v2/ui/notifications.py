import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_notification(project_name: str, message: str, level: str = "INFO", output_dir="outputs"):
    """
    Appends notification to outputs/<project>/notifications.log
    """
    try:
        log_path = os.path.join(output_dir, project_name, "notifications.log")
        ts = datetime.utcnow().isoformat()
        with open(log_path, "a") as f:
            f.write(f"[{ts}] [{level}] {message}\n")
    except Exception as e:
        logger.error(f"Failed to log notification: {e}")

def send_desktop_notification(title: str, message: str):
    """
    Best-effort desktop notification using plyer.
    """
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Repo Intel Orchestrator",
            timeout=10
        )
    except ImportError:
        pass # Plyer not installed
    except Exception:
        pass # Notification failed (headless env, etc.)
