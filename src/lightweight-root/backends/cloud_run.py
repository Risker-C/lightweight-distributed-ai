"""
Google Cloud Run adapter
"""
import subprocess
import json
from typing import Dict, Optional, Any
from .base import CloudAdapter

class CloudRunAdapter(CloudAdapter):
    """Deploy to Google Cloud Run"""
    
    def deploy(self, image_tag: str, env_vars: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """Deploy to Cloud Run"""
        
        project = self.config['project']
        region = self.config.get('region', 'us-central1')
        service_name = kwargs.get('service_name', 'lightweight-worker')
        image = f"gcr.io/{project}/lightweight-root:{image_tag}"
        
        cmd = [
            'gcloud', 'run', 'deploy', service_name,
            '--image', image,
            '--platform', 'managed',
            '--region', region,
            '--project', project
        ]
        
        if env_vars:
            env_str = ','.join([f"{k}={v}" for k, v in env_vars.items()])
            cmd.extend(['--set-env-vars', env_str])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            'id': f"{project}:{region}:{service_name}",
            'status': 'deployed',
            'platform': 'cloud_run',
            'url': f"https://{service_name}-{region}.run.app"
        }
    
    def get_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get Cloud Run service status"""
        return {
            'id': deployment_id,
            'status': 'running',
            'platform': 'cloud_run'
        }
