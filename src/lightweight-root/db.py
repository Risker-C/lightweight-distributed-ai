"""
SQLite database for job management
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_path='data/jobs.db'):
        self.db_path = db_path
        # Ensure data directory exists
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                payload TEXT,
                status TEXT NOT NULL,
                backend TEXT NOT NULL,
                backend_run_id TEXT,
                result TEXT,
                error_msg TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_job(self, job_id: str, job_type: str, payload: Dict, backend: str):
        """Create a new job"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.utcnow().isoformat()
        conn.execute(
            'INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (job_id, job_type, json.dumps(payload), 'pending', backend, None, None, None, now, now)
        )
        conn.commit()
        conn.close()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_jobs_by_status(self, status: str) -> List[Dict]:
        """Get all jobs with given status"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('SELECT * FROM jobs WHERE status = ?', (status,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_job(self, job_id: str, **kwargs):
        """Update job fields"""
        conn = sqlite3.connect(self.db_path)
        kwargs['updated_at'] = datetime.utcnow().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [job_id]
        
        conn.execute(f'UPDATE jobs SET {set_clause} WHERE id = ?', values)
        conn.commit()
        conn.close()
