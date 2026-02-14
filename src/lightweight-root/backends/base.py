"""
Base class for cloud deployment adapters
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class CloudAdapter(ABC):
    """Abstract base class for cloud platform adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def deploy(self, image_tag: str, env_vars: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Deploy a Docker image to the cloud platform
        
        Args:
            image_tag: Docker image tag to deploy
            env_vars: Environment variables for the container
            **kwargs: Platform-specific parameters
            
        Returns:
            Dict with deployment info (id, url, status, etc.)
        """
        pass
    
    @abstractmethod
    def get_status(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get deployment status
        
        Args:
            deployment_id: Deployment identifier
            
        Returns:
            Dict with status info
        """
        pass
