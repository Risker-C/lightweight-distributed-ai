"""
GitHub Actions adapter for workflow triggers
"""
import requests
from typing import Dict, Optional, Any
from .base import CloudAdapter

class GitHubActionsAdapter(CloudAdapter):
    """Trigger GitHub Actions workflows"""
    
    def deploy(self, image_tag: str, env_vars: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """Trigger GitHub workflow dispatch"""
        
        repo = self.config['repository']  # format: owner/repo
        workflow = self.config['workflow']  # e.g., worker.yml
        token = self.config['token']
        
        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        payload = {
            'ref': self.config.get('ref', 'main'),
            'inputs': {
                'image_tag': image_tag,
                'env_vars': str(env_vars or {}),
                **(kwargs.get('inputs', {}))
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        return {
            'id': f"{repo}:{workflow}:{image_tag}",
            'status': 'triggered',
            'platform': 'github_actions'
        }
    
    def get_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get workflow run status (simplified)"""
        return {
            'id': deployment_id,
            'status': 'running',
            'platform': 'github_actions'
        }
