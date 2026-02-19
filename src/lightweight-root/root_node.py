#!/usr/bin/env python3
"""
Root Node - Manages and distributes tasks to workers
"""
from flask import Flask, jsonify, request
import os
import sys
import requests
import threading
import time
from datetime import datetime

print("=" * 50, file=sys.stderr)
print("Starting Root Node", file=sys.stderr)
print("=" * 50, file=sys.stderr)

app = Flask(__name__)

# Worker registry
workers = {}  # {worker_id: {url, status, last_heartbeat, tasks_completed, ...}}
worker_lock = threading.Lock()

# Root node stats
root_stats = {
    'started_at': datetime.utcnow().isoformat(),
    'total_tasks_distributed': 0,
    'active_workers': 0
}

def health_check_worker(worker_id, worker_url):
    """Check worker health"""
    try:
        response = requests.get(f"{worker_url}/health", timeout=5)
        if response.status_code == 200:
            with worker_lock:
                if worker_id in workers:
                    workers[worker_id]['status'] = 'online'
                    workers[worker_id]['last_heartbeat'] = datetime.utcnow().isoformat()
            return True
    except Exception as e:
        print(f"Worker {worker_id} health check failed: {e}", file=sys.stderr)
        with worker_lock:
            if worker_id in workers:
                workers[worker_id]['status'] = 'offline'
    return False

def heartbeat_monitor():
    """Monitor worker health periodically"""
    print("Heartbeat monitor started", file=sys.stderr)
    while True:
        time.sleep(30)  # Check every 30 seconds
        with worker_lock:
            worker_list = list(workers.items())
        
        for worker_id, worker_info in worker_list:
            health_check_worker(worker_id, worker_info['url'])

# Start heartbeat monitor
monitor_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
monitor_thread.start()

@app.route('/')
def root():
    return jsonify({
        'service': 'root-node',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': ['/', '/health', '/workers', '/workers/register', '/distribute']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'root-node'
    })

@app.route('/workers', methods=['GET'])
def list_workers():
    """List all registered workers"""
    with worker_lock:
        worker_list = list(workers.values())
        active_count = sum(1 for w in worker_list if w['status'] == 'online')
    
    return jsonify({
        'workers': worker_list,
        'total': len(worker_list),
        'active': active_count
    })

@app.route('/workers/register', methods=['POST'])
def register_worker():
    """Register a new worker"""
    data = request.get_json() or {}
    worker_url = data.get('url')
    worker_name = data.get('name', 'unnamed-worker')
    
    if not worker_url:
        return jsonify({'error': 'Worker URL required'}), 400
    
    # Generate worker ID
    worker_id = f"{worker_name}-{len(workers)}"
    
    # Check worker health
    if not health_check_worker(worker_id, worker_url):
        return jsonify({'error': 'Worker health check failed'}), 400
    
    worker_info = {
        'id': worker_id,
        'name': worker_name,
        'url': worker_url,
        'status': 'online',
        'registered_at': datetime.utcnow().isoformat(),
        'last_heartbeat': datetime.utcnow().isoformat(),
        'tasks_assigned': 0
    }
    
    with worker_lock:
        workers[worker_id] = worker_info
        root_stats['active_workers'] = sum(1 for w in workers.values() if w['status'] == 'online')
    
    print(f"Worker registered: {worker_id} at {worker_url}", file=sys.stderr)
    
    return jsonify({
        'id': worker_id,
        'status': 'registered',
        'message': 'Worker registered successfully'
    }), 201

@app.route('/distribute', methods=['POST'])
def distribute_task():
    """Distribute task to an available worker"""
    data = request.get_json() or {}
    
    # Find an online worker
    with worker_lock:
        online_workers = [w for w in workers.values() if w['status'] == 'online']
    
    if not online_workers:
        return jsonify({'error': 'No workers available'}), 503
    
    # Simple round-robin: pick worker with least tasks
    target_worker = min(online_workers, key=lambda w: w.get('tasks_assigned', 0))
    
    # Send task to worker
    try:
        response = requests.post(
            f"{target_worker['url']}/tasks",
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            with worker_lock:
                workers[target_worker['id']]['tasks_assigned'] += 1
                root_stats['total_tasks_distributed'] += 1
            
            result = response.json()
            result['worker_id'] = target_worker['id']
            result['worker_url'] = target_worker['url']
            
            print(f"Task distributed to {target_worker['id']}", file=sys.stderr)
            
            return jsonify(result), 201
        else:
            return jsonify({'error': 'Worker rejected task'}), 500
            
    except Exception as e:
        print(f"Failed to distribute task: {e}", file=sys.stderr)
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get root node statistics"""
    with worker_lock:
        current_stats = root_stats.copy()
        current_stats['total_workers'] = len(workers)
        current_stats['active_workers'] = sum(1 for w in workers.values() if w['status'] == 'online')
    
    return jsonify(current_stats)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Root Node on 0.0.0.0:{port}", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False)
