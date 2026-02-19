#!/usr/bin/env python3
"""
Enhanced Flask app with code execution capabilities
"""
from flask import Flask, jsonify, request
import os
import sys
import time
import threading
import queue
import uuid
import subprocess
import tempfile
from datetime import datetime
from monitoring import Monitor, Logger
from version import VERSION

print("=" * 50, file=sys.stderr)
print(f"Starting Lightweight AI Worker v{VERSION} - Code Execution", file=sys.stderr)
print("=" * 50, file=sys.stderr)

app = Flask(__name__)

# Initialize monitoring and logging
monitor = Monitor()
logger = Logger('worker')

# Task queue and storage
task_queue = queue.Queue()
tasks = {}
task_lock = threading.Lock()

# Worker stats
stats = {
    'started_at': datetime.utcnow().isoformat(),
    'tasks_completed': 0,
    'tasks_failed': 0,
    'tasks_pending': 0
}

def execute_code(language, code, input_data=None):
    """Execute code in specified language"""
    try:
        if language == 'python':
            return execute_python(code, input_data)
        elif language == 'javascript' or language == 'node':
            return execute_javascript(code, input_data)
        elif language == 'bash' or language == 'shell':
            return execute_bash(code, input_data)
        else:
            return {'error': f'Unsupported language: {language}'}
    except Exception as e:
        return {'error': str(e)}

def execute_python(code, input_data=None):
    """Execute Python code"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        env = os.environ.copy()
        if input_data:
            env['INPUT_DATA'] = str(input_data)
        
        print(f"[EXEC DEBUG] Starting subprocess to execute Python code", flush=True)
        start_time = time.time()
        
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        elapsed = time.time() - start_time
        print(f"[EXEC DEBUG] Subprocess completed in {elapsed:.2f}s, returncode={result.returncode}", flush=True)
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    finally:
        os.unlink(temp_file)

def execute_javascript(code, input_data=None):
    """Execute JavaScript code"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        if input_data:
            f.write(f"const INPUT_DATA = {input_data};\n")
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['node', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    except FileNotFoundError:
        return {'error': 'Node.js not installed'}
    finally:
        os.unlink(temp_file)

def execute_bash(code, input_data=None):
    """Execute Bash script"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write('#!/bin/bash\n')
        if input_data:
            f.write(f'INPUT_DATA="{input_data}"\n')
        f.write(code)
        temp_file = f.name
    
    try:
        os.chmod(temp_file, 0o755)
        result = subprocess.run(
            ['/bin/bash', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    finally:
        os.unlink(temp_file)

def task_worker():
    """Background worker to process tasks"""
    logger.info("Task worker started")
    while True:
        try:
            task_id = task_queue.get(timeout=1)
            with task_lock:
                if task_id not in tasks:
                    continue
                tasks[task_id]['status'] = 'processing'
                tasks[task_id]['started_at'] = datetime.utcnow().isoformat()
            
            task_data = tasks[task_id]
            task_type = task_data.get('type', 'default')
            payload = task_data.get('payload', {})
            
            logger.info(f"Processing task {task_id}: {task_type}")
            
            # Execute task based on type
            result = execute_task(task_type, payload)
            
            with task_lock:
                tasks[task_id]['status'] = 'completed'
                tasks[task_id]['result'] = result
                tasks[task_id]['completed_at'] = datetime.utcnow().isoformat()
                stats['tasks_completed'] += 1
                stats['tasks_pending'] -= 1
            
            logger.info(f"Task {task_id} completed")
            
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Task error: {e}")
            with task_lock:
                if task_id in tasks:
                    tasks[task_id]['status'] = 'failed'
                    tasks[task_id]['error'] = str(e)
                    stats['tasks_failed'] += 1
                    stats['tasks_pending'] -= 1

def execute_task(task_type, payload):
    """Execute different types of tasks"""
    if task_type == 'code':
        # Code execution task
        language = payload.get('language', 'python')
        code = payload.get('code', '')
        input_data = payload.get('input')
        
        return execute_code(language, code, input_data)
    
    elif task_type == 'compute':
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
        duration = payload.get('duration', 1)
        time.sleep(duration)
        return {'slept': duration}
    
    elif task_type == 'echo':
        return {'echo': payload.get('message', 'hello')}
    
    return {'result': 'unknown task type'}

def metrics_collector():
    """Collect metrics periodically"""
    while True:
        time.sleep(10)
        monitor.collect_metrics()

# Start threads
worker_thread = threading.Thread(target=task_worker, daemon=True)
worker_thread.start()

metrics_thread = threading.Thread(target=metrics_collector, daemon=True)
metrics_thread.start()

# Routes
@app.route('/')
def root():
    return jsonify({
        'service': 'lightweight-ai-worker',
        'status': 'running',
        'version': '2.2.0',
        'features': ['task-scheduling', 'distributed-computing', 'code-execution'],
        'supported_languages': ['python', 'javascript', 'bash'],
        'endpoints': ['/', '/health', '/ping', '/tasks', '/tasks/<id>', '/stats', '/metrics', '/logs']
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'lightweight-ai-worker',
        'version': '2.2.0'
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
    logger.info(f"Task created: {task_id}")
    
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
    
    task_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
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
    logger.info(f"Starting Flask on 0.0.0.0:{port}")
    logger.info("Code execution support: Python, JavaScript, Bash")
    app.run(host='0.0.0.0', port=port, debug=False)
