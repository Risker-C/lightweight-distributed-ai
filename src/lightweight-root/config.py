"""
Configuration management
"""
import os
import json

def load_config():
    """Load configuration from environment or file"""
    config_path = os.getenv('CONFIG_PATH', 'config.json')
    
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    
    # Default config from environment
    return {
        'oracle_cloud': {
            'compartment_id': os.getenv('OCI_COMPARTMENT_ID'),
            'ocir_repository': os.getenv('OCIR_REPOSITORY'),
            'subnet_id': os.getenv('OCI_SUBNET_ID'),
            'region': os.getenv('OCI_REGION', 'us-ashburn-1')
        },
        'github_actions': {
            'repository': os.getenv('GITHUB_REPO'),
            'workflow': os.getenv('GITHUB_WORKFLOW', 'worker.yml'),
            'token': os.getenv('GITHUB_TOKEN'),
            'ref': os.getenv('GITHUB_REF', 'main')
        }
    }
