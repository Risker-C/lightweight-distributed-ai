"""
Job scheduler
"""
import time
from db import Database
from backends.oracle_cloud import OracleCloudAdapter
from backends.github_actions import GitHubActionsAdapter
from config import load_config

class Scheduler:
    def __init__(self):
        self.db = Database()
        self.config = load_config()
        self.backends = {
            'oracle_cloud': OracleCloudAdapter(self.config['oracle_cloud']),
            'github_actions': GitHubActionsAdapter(self.config['github_actions'])
        }
    
    def run(self):
        """Main scheduler loop"""
        while True:
            try:
                self.process_pending_jobs()
                self.check_running_jobs()
                time.sleep(5)  # Poll every 5 seconds
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(10)
    
    def process_pending_jobs(self):
        """Dispatch pending jobs to cloud"""
        jobs = self.db.get_jobs_by_status('pending')
        
        for job in jobs:
            try:
                backend = self.backends.get(job['backend'])
                if not backend:
                    continue
                
                # Deploy to cloud
                result = backend.deploy(
                    image_tag=job.get('image_tag', 'latest'),
                    env_vars=job.get('env_vars')
                )
                
                # Update job status
                self.db.update_job(
                    job['id'],
                    status='running',
                    backend_run_id=result['id']
                )
            except Exception as e:
                self.db.update_job(job['id'], status='failed', error_msg=str(e))
    
    def check_running_jobs(self):
        """Check status of running jobs"""
        jobs = self.db.get_jobs_by_status('running')
        
        for job in jobs:
            try:
                backend = self.backends.get(job['backend'])
                if not backend:
                    continue
                
                status = backend.get_status(job['backend_run_id'])
                
                if status['status'] in ['success', 'completed']:
                    self.db.update_job(job['id'], status='success')
                elif status['status'] in ['failed', 'error']:
                    self.db.update_job(job['id'], status='failed')
            except Exception as e:
                print(f"Error checking job {job['id']}: {e}")
