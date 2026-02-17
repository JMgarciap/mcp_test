import base64
import logging
import os
import requests
from typing import List, Optional, Tuple, Dict, Any
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token: str, api_base_url: Optional[str] = None):
        self.token = token
        self.api_base_url = api_base_url or "https://api.github.com"
        # Ensure no trailing slash
        self.api_base_url = self.api_base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        self._tree_cache = {}

    def _get_api_url(self, repo_url: str) -> str:
        """Determines the API base URL for a given repo URL."""
        # If the user explicitly provided an API base URL (e.g. for Enterprise), use it.
        # Otherwise, default to public GitHub API.
        # In a more advanced implementation, we might try to infer from the repo_url
        # if no env var is set, but the requirements say to use env var or default.
        return self.api_base_url

    def parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """Parses owner and repo name from a URL."""
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError(f"Invalid repository URL: {repo_url}")
        return path_parts[-2], path_parts[-1].replace(".git", "")

    def get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetches repository metadata."""
        url = f"{self.api_base_url}/repos/{owner}/{repo}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def list_tree(self, owner: str, repo: str, ref: str) -> List[str]:
        """Lists all files in the repository recursively."""
        cache_key = f"{owner}/{repo}@{ref}"
        if cache_key in self._tree_cache:
            return self._tree_cache[cache_key]

        # Use the git tree API for recursive listing
        # https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28#get-a-tree
        url = f"{self.api_base_url}/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("truncated", False):
                logger.warning(f"Tree for {owner}/{repo}@{ref} is truncated.")

            files = [item["path"] for item in data.get("tree", []) if item["type"] == "blob"]
            self._tree_cache[cache_key] = files
            return files
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to list tree for {owner}/{repo}@{ref}: {e}")
            raise

    def read_file(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Reads the content of a file."""
        # Use the contents API
        # https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "content" not in data:
                return "" # Handle empty or size 0 files gracefully if api returns no content field
            
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return "" # File not found, treat as empty or missing
            logger.error(f"Failed to read file {path} in {owner}/{repo}@{ref}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error decoding file {path}: {e}")
            return "" # Return empty on decode error
