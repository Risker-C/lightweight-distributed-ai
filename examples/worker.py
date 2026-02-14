"""
Example worker script for GitHub Actions
"""
import json
import os
import sys

def main():
    # Get environment variables
    env_vars_str = os.getenv('ENV_VARS', '{}')
    env_vars = json.loads(env_vars_str)
    
    print(f"Worker started with env vars: {env_vars}")
    
    # Do your work here
    # Example: AI inference, data processing, etc.
    
    result = {
        'status': 'success',
        'message': 'Task completed',
        'data': env_vars
    }
    
    # Save results
    os.makedirs('results', exist_ok=True)
    with open('results/output.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Worker completed successfully")

if __name__ == '__main__':
    main()
