"""
Flask API for job management
"""
from flask import Flask, request, jsonify
from db import Database
import uuid

def create_app():
    app = Flask(__name__)
    db = Database()
    
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
