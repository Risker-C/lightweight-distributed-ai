#!/usr/bin/env python3
"""
Enhanced Monitoring Module - Tracks Main Process + Child Processes
Version 2.2 - Improved to capture all resource usage including subprocesses
"""
import time
import psutil
import os
from datetime import datetime
from collections import deque

class Monitor:
    """Monitor main process and all child processes"""
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
    
    def get_all_processes(self):
        """Get main process and all children"""
        processes = [self.process]
        try:
            children = self.process.children(recursive=True)
            processes.extend(children)
        except psutil.NoSuchProcess:
            pass
        return processes
    
    def collect_metrics(self):
        """Collect metrics from all processes (main + children)"""
        try:
            processes = self.get_all_processes()
            
            # DEBUG: Log process count
            print(f"[MONITOR DEBUG] Found {len(processes)} total processes (1 main + {len(processes)-1} children)", flush=True)
            
            # Aggregate metrics from all processes
            total_cpu = 0
            total_memory = 0
            total_threads = 0
            child_count = len(processes) - 1
            
            proc_details = []
            
            for proc in processes:
                try:
                    cpu = proc.cpu_percent(interval=0.1)
                    memory = proc.memory_info().rss / 1024 / 1024
                    threads = proc.num_threads()
                    
                    # DEBUG: Log each process
                    print(f"[MONITOR DEBUG] PID {proc.pid}: CPU={cpu:.2f}%, Memory={memory:.2f}MB, Threads={threads}", flush=True)
                    
                    total_cpu += cpu
                    total_memory += memory
                    total_threads += threads
                    
                    proc_details.append({
                        'pid': proc.pid,
                        'parent_pid': proc.ppid(),
                        'cpu_percent': round(cpu, 2),
                        'memory_mb': round(memory, 2),
                        'threads': threads
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"[MONITOR DEBUG] Error accessing process: {e}", flush=True)
            
            # DEBUG: Log aggregated metrics
            print(f"[MONITOR DEBUG] Total: CPU={total_cpu:.2f}%, Memory={total_memory:.2f}MB, Children={child_count}", flush=True)
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': round(total_cpu, 2),
                'memory_mb': round(total_memory, 2),
                'threads': total_threads,
                'child_processes': child_count,
                'process_details': proc_details[:10],  # Limit to top 10
                'uptime_seconds': int(time.time() - self.start_time)
            }
            
            self.metrics_history.append(metrics)
            return metrics
        except Exception as e:
            print(f"[MONITOR ERROR] collect_metrics failed: {e}", flush=True)
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
        child_counts = [m['child_processes'] for m in self.metrics_history if 'child_processes' in m]
        
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
            'child_processes': {
                'current': child_counts[-1] if child_counts else 0,
                'max': max(child_counts) if child_counts else 0
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
