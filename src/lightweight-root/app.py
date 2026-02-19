#!/usr/bin/env python3
"""
Minimal Flask app for testing - guaranteed to work
"""
from flask import Flask, jsonify
import os
import sys

print("=" * 50, file=sys.stderr)
print("Starting Lightweight AI Worker", file=sys.stderr)
print("=" * 50, file=sys.stderr)

app = Flask(__name__)

@app.route('/')
def root():
    print("Root endpoint accessed", file=sys.stderr)
    return jsonify({
        'service': 'lightweight-ai-worker',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': ['/', '/health', '/ping']
    })

@app.route('/health')
def health():
    print("Health check accessed", file=sys.stderr)
    return jsonify({
        'status': 'healthy',
        'service': 'lightweight-ai-worker'
    })

@app.route('/ping')
def ping():
    return jsonify({'pong': True})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"Starting Flask on 0.0.0.0:{port}", file=sys.stderr)
    app.run(host='0.0.0.0', port=port, debug=False)
