"""
Main entry point for lightweight root node
"""
import os
import sys
from api import create_app
from scheduler import Scheduler
import threading

def main():
    # Create Flask app
    app = create_app()
    
    # Start scheduler in background thread
    scheduler = Scheduler()
    scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
    scheduler_thread.start()
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
