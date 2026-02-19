#!/usr/bin/env python3
"""
Enhanced monitoring that tracks child processes
"""
import psutil
import os
import time
from datetime import datetime
from collections import deque

class EnhancedMonitor:
    """Monitor main process and all children"""
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.start_time = time.time()
        self.main_process = psutil.Process(os.getpid())
    
    def collect_metrics(self):
        """Collect metrics including child processes"""
        try:
            # Main process metrics
            main_cpu = self.main_process.cpu_percent(interval=0.1)
            main_mem = self.main_process.memory_info().rss / 1024 / 1024
            
            # Child processes metrics
            children = self.main_process.children(recursive=True)
            child_cpu = sum(c.cpu_percent() for c in children)
            child_mem = sum(c.memory_info().rss / 1024 / 1024 for c in children)
            
            # Total metrics
            total_cpu = main_cpu + child_cpu
            total_mem = main_mem + child_mem
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'main': {
                    'cpu_percent': round(main_cpu, 2),
                    'memory_mb': round(main_mem, 2)
                },
                'children': {
                    'count': len(children),
                    'cpu_percent': round(child_cpu, 2),
                    'memory_mb': round(child_mem, 2)
                },
                'total': {
                    'cpu_percent': round(total_cpu, 2),
                    'memory_mb': round(total_mem, 2)
                },
                'uptime_seconds': int(time.time() - self.start_time)
            }
            
            self.metrics_history.append(metrics)
            return metrics
        except Exception as e:
            return {'error': str(e)}
    
    def get_summary(self):
        """Get summary including child processes"""
        if not self.metrics_history:
            return {}
        
        total_cpu = [m['total']['cpu_percent'] for m in self.metrics_history if 'total' in m]
        total_mem = [m['total']['memory_mb'] for m in self.metrics_history if 'total' in m]
        
        return {
            'uptime_seconds': int(time.time() - self.start_time),
            'cpu': {
                'current': total_cpu[-1] if total_cpu else 0,
                'avg': round(sum(total_cpu) / len(total_cpu), 2) if total_cpu else 0,
                'max': max(total_cpu) if total_cpu else 0
            },
            'memory': {
                'current_mb': total_mem[-1] if total_mem else 0,
                'avg_mb': round(sum(total_mem) / len(total_mem), 2) if total_mem else 0,
                'max_mb': max(total_mem) if total_mem else 0
            },
            'samples': len(self.metrics_history)
        }
