"""
Oracle Cloud adapter for container deployment
"""
import subprocess
import json
from typing import Dict, Optional, Any
from .base import CloudAdapter

class OracleCloudAdapter(CloudAdapter):
    """Deploy containers to Oracle Cloud Container Instances"""
    
    def deploy(self, image_tag: str, env_vars: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """Deploy to Oracle Cloud Container Instance"""
        
        compartment_id = self.config['compartment_id']
        ocir_repo = self.config['ocir_repository']
        region = self.config.get('region', 'us-ashburn-1')
        
        # Push image to OCIR
        ocir_image = f"{region}.ocir.io/{ocir_repo}:{image_tag}"
        subprocess.run(['docker', 'tag', f'lightweight-root:{image_tag}', ocir_image], check=True)
        subprocess.run(['docker', 'push', ocir_image], check=True)
        
        # Create container instance
        container_config = {
            'compartmentId': compartment_id,
            'containers': [{
                'imageUrl': ocir_image,
                'environmentVariables': env_vars or {}
            }],
            'vnics': [{'subnetId': self.config['subnet_id']}],
            'shape': self.config.get('shape', 'CI.Standard.E4.Flex'),
            'shapeConfig': {'ocpus': 1, 'memoryInGBs': 1}
        }
        
        result = subprocess.run(
            ['oci', 'container-instances', 'container-instance', 'create', '--from-json', json.dumps(container_config)],
            capture_output=True, text=True, check=True
        )
        
        instance_data = json.loads(result.stdout)
        return {
            'id': instance_data['data']['id'],
            'status': instance_data['data']['lifecycle-state'],
            'platform': 'oracle_cloud'
        }
    
    def get_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get container instance status"""
        result = subprocess.run(
            ['oci', 'container-instances', 'container-instance', 'get', '--container-instance-id', deployment_id],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        return {
            'id': deployment_id,
            'status': data['data']['lifecycle-state'],
            'platform': 'oracle_cloud'
        }
