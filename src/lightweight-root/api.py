"""
Flask API for job management
"""
from flask import Flask, request, jsonify
from db import Database
import uuid

def create_app():
    app = Flask(__name__)
    db = Database()
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            'service': 'lightweight-ai-worker',
            'status': 'running',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        import psutil
        import os
        return jsonify({
            'status': 'healthy',
            'memory_mb': round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 1),
            'uptime_seconds': int(psutil.Process(os.getpid()).create_time())
        })
    
    @app.route('/jobs', methods=['POST'])
    def create_job():
        """Create a new job"""
        data = request.json
        job_id = str(uuid.uuid4())
        
        db.create_job(
            job_id=job_id,
            job_type=data.get('type', 'default'),
            payload=data.get('payload', {}),
            backend=data.get('backend', 'oracle_cloud')
        )
        
        return jsonify({'id': job_id, 'status': 'pending'}), 201
    
    @app.route('/jobs/<job_id>', methods=['GET'])
    def get_job(job_id):
        """Get job status"""
        job = db.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(job)
    
    @app.route('/jobs/<job_id>/result', methods=['GET'])
    def get_result(job_id):
        """Get job result"""
        job = db.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job['status'] != 'success':
            return jsonify({'error': 'Job not completed'}), 400
        
        return jsonify({'result': job.get('result')})
    
    return app
