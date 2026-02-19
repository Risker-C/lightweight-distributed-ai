#!/usr/bin/env python3
"""
Enhanced Flask app with task scheduling, distributed computing, and monitoring
"""
from flask import Flask, jsonify, request
import os
import sys
import time
import threading
import queue
import uuid
from datetime import datetime
from monitoring import Monitor, Logger

print("=" * 50, file=sys.stderr)
print("Starting Lightweight AI Worker v2.0", file=sys.stderr)
print("=" * 50, file=sys.stderr)

app = Flask(__name__)

# Initialize monitoring and logging
monitor = Monitor()
logger = Logger('worker')

# Task queue and storage
task_queue = queue.Queue()
tasks = {}  # {task_id: {status, result, created_at, ...}}
task_lock = threading.Lock()

# Worker stats
stats = {
    'started_at': datetime.utcnow().isoformat(),
    'tasks_completed': 0,
    'tasks_failed': 0,
    'tasks_pending': 0
}

def metrics_collector():
    """Collect metrics periodically"""
    while True:
        time.sleep(10)  # Collect every 10 seconds
        monitor.collect_metrics()

# Start metrics collector
metrics_thread = threading.Thread(target=metrics_collector, daemon=True)
metrics_thread.start()

def task_worker():
    """Background worker to process tasks"""
    print("Task worker started", file=sys.stderr)
    while True:
        try:
            task_id = task_queue.get(timeout=1)
            with task_lock:
                if task_id not in tasks:
                    continue
                tasks[task_id]['status'] = 'processing'
                tasks[task_id]['started_at'] = datetime.utcnow().isoformat()
            
            # Simulate task processing
            task_data = tasks[task_id]
            task_type = task_data.get('type', 'default')
            payload = task_data.get('payload', {})
            
            print(f"Processing task {task_id}: {task_type}", file=sys.stderr)
            
            # Execute task based on type
            result = execute_task(task_type, payload)
            
            with task_lock:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['result'] = result
                tasks[task_id]['completed_at'] = datetime.utcnow().isoformat()
                stats['tasks_completed'] += 1
                stats['tasks_pending'] -= 1
            
            print(f"Task {task_id} completed", file=sys.stderr)
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Task error: {e}", file=sys.stderr)
            with task_lock:
                if task_id in tasks:
                    tasks[task_id]['status'] = 'failed'
                    tasks[task_id]['error'] = str(e)
                    stats['tasks_failed'] += 1
                    stats['tasks_pending'] -= 1

def execute_task(task_type, payload):
    """Execute different types of tasks"""
    if task_type == 'compute':
        # Simple computation task
        operation = payload.get('operation', 'add')
        numbers = payload.get('numbers', [1, 2, 3])
        
        if operation == 'add':
            return {'result': sum(numbers)}
        elif operation == 'multiply':
            result = 1
            for n in numbers:
                result *= n
            return {'result': result}
        elif operation == 'factorial':
            n = payload.get('number', 5)
            result = 1
            for i in range(1, n + 1):
                result *= i
            return {'result': result}
    
    elif task_type == 'sleep':
        # Sleep task for testing
        duration = payload.get('duration', 1)
        time.sleep(duration)
        return {'slept': duration}
    
    elif task_type == 'echo':
        # Echo task
        return {'echo': payload.get('message', 'hello')}
    
    return {'result': 'unknown task type'}

# Start worker thread
worker_thread = threading.Thread(target=task_worker, daemon=True)
worker_thread.start()

# Routes
@app.route('/')
def root():
    return jsonify({
        'service': 'lightweight-ai-worker',
        'status': 'running',
        'version': '2.0.0',
        'features': ['task-scheduling', 'distributed-computing'],
        'endpoints': ['/', '/health', '/ping', '/tasks', '/tasks/<id>', '/stats']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'lightweight-ai-worker',
        'version': '2.0.0'
    })

@app.route('/ping')
def ping():
    return jsonify({'pong': True, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json() or {}
    task_id = str(uuid.uuid4())
    
    task = {
        'id': task_id,
        'type': data.get('type', 'echo'),
        'payload': data.get('payload', {}),
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat()
    }
    
    with task_lock:
        tasks[task_id] = task
        stats['tasks_pending'] += 1
    
    task_queue.put(task_id)
    
    print(f"Task created: {task_id}", file=sys.stderr)
    
    return jsonify({
        'id': task_id,
        'status': 'pending',
        'message': 'Task queued successfully'
    }), 201

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task status and result"""
    with task_lock:
        task = tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """List all tasks"""
    with task_lock:
        task_list = list(tasks.values())
    
    # Sort by created_at, newest first
    task_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Limit to last 100 tasks
    return jsonify({
        'tasks': task_list[:100],
        'total': len(task_list)
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get worker statistics"""
    with task_lock:
        current_stats = stats.copy()
        current_stats['total_tasks'] = len(tasks)
    
    # Add monitoring data
    current_stats['monitoring'] = monitor.get_summary()
    
    return jsonify(current_stats)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get detailed metrics"""
    limit = request.args.get('limit', 100, type=int)
    return jsonify({
        'current': monitor.get_metrics(),
        'history': monitor.get_history(limit),
        'summary': monitor.get_summary()
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get application logs"""
    level = request.args.get('level')
    limit = request.args.get('limit', 100, type=int)
    return jsonify({
        'logs': logger.get_logs(level, limit)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"Starting Flask on 0.0.0.0:{port}", file=sys.stderr)
    print(f"Task worker ready", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False)
