#!/usr/bin/env python3
"""
Monitoring and Logging Module
"""
import time
import psutil
import os
from datetime import datetime
from collections import deque

class Monitor:
    """System monitoring"""
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
    
    def collect_metrics(self):
        """Collect current system metrics"""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': round(cpu_percent, 2),
                'memory_mb': round(memory_mb, 2),
                'uptime_seconds': int(time.time() - self.start_time),
                'threads': self.process.num_threads()
            }
            
            self.metrics_history.append(metrics)
            return metrics
        except Exception as e:
            return {'error': str(e)}
    
    def get_metrics(self):
        """Get current metrics"""
        return self.collect_metrics()
    
    def get_history(self, limit=None):
        """Get metrics history"""
        if limit:
            return list(self.metrics_history)[-limit:]
        return list(self.metrics_history)
    
    def get_summary(self):
        """Get metrics summary"""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m['cpu_percent'] for m in self.metrics_history if 'cpu_percent' in m]
        mem_values = [m['memory_mb'] for m in self.metrics_history if 'memory_mb' in m]
        
        return {
            'uptime_seconds': int(time.time() - self.start_time),
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'avg': round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current_mb': mem_values[-1] if mem_values else 0,
                'avg_mb': round(sum(mem_values) / len(mem_values), 2) if mem_values else 0,
                'max_mb': max(mem_values) if mem_values else 0
            },
            'samples': len(self.metrics_history)
        }

class Logger:
    """Simple structured logger"""
    def __init__(self, name='app'):
        self.name = name
        self.logs = deque(maxlen=1000)
    
    def log(self, level, message, **kwargs):
        """Log a message"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'name': self.name,
            'message': message,
            **kwargs
        }
        self.logs.append(log_entry)
        print(f"[{level}] {message}", flush=True)
        return log_entry
    
    def info(self, message, **kwargs):
        return self.log('INFO', message, **kwargs)
    
    def warning(self, message, **kwargs):
        return self.log('WARNING', message, **kwargs)
    
    def error(self, message, **kwargs):
        return self.log('ERROR', message, **kwargs)
    
    def get_logs(self, level=None, limit=100):
        """Get recent logs"""
        logs = list(self.logs)
        if level:
            logs = [l for l in logs if l['level'] == level]
        return logs[-limit:]
