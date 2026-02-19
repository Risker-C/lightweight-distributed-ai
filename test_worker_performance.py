#!/usr/bin/env python3
"""
Worker Performance Test - Verify real computation
"""
import requests
import time
import json

RAILWAY_URL = "https://lightweight-distributed-ai-production.up.railway.app"
KOYEB_URL = "https://naughty-carina-risker666-8ce36d54.koyeb.app"

def submit_task(worker_url, code, language="python"):
    """Submit a task to worker"""
    response = requests.post(
        f"{worker_url}/tasks",
        json={
            "type": "code",
            "payload": {
                "language": language,
                "code": code
            }
        }
    )
    return response.json()

def get_task_result(worker_url, task_id, max_wait=30):
    """Wait for task completion and get result"""
    start = time.time()
    while time.time() - start < max_wait:
        response = requests.get(f"{worker_url}/tasks/{task_id}")
        data = response.json()
        if data['status'] == 'completed':
            return data
        time.sleep(1)
    return None

def test_cpu_intensive():
    """Test CPU-intensive computation"""
    print("\n=== Test 1: CPU-Intensive Computation ===")
    
    code = """
import time
import os

print(f"Process PID: {os.getpid()}")
print(f"Parent PID: {os.getppid()}")

start = time.time()

# CPU-intensive: Calculate prime numbers
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [n for n in range(2, 50000) if is_prime(n)]

end = time.time()

print(f"Found {len(primes)} primes")
print(f"Computation time: {end - start:.2f}s")
print(f"First 10 primes: {primes[:10]}")
print(f"Last 10 primes: {primes[-10:]}")
"""
    
    print("Submitting task to Railway Worker...")
    result = submit_task(RAILWAY_URL, code)
    task_id = result['id']
    print(f"Task ID: {task_id}")
    
    print("Waiting for completion...")
    final_result = get_task_result(RAILWAY_URL, task_id)
    
    if final_result:
        print("\n✅ Task completed!")
        print(final_result['result']['stdout'])
    else:
        print("\n❌ Task timeout")

def test_memory_intensive():
    """Test memory-intensive computation"""
    print("\n=== Test 2: Memory-Intensive Computation ===")
    
    code = """
import time
import sys

print("Creating large data structures...")
start = time.time()

# Create large lists
data = []
for i in range(1000000):
    data.append([i, i*2, i*3, i*4, i*5])

end = time.time()

print(f"Created list with {len(data)} elements")
print(f"Memory usage: {sys.getsizeof(data) / 1024 / 1024:.2f}MB")
print(f"Time: {end - start:.2f}s")
"""
    
    print("Submitting task to Koyeb Worker...")
    result = submit_task(KOYEB_URL, code)
    task_id = result['id']
    print(f"Task ID: {task_id}")
    
    print("Waiting for completion...")
    final_result = get_task_result(KOYEB_URL, task_id)
    
    if final_result:
        print("\n✅ Task completed!")
        print(final_result['result']['stdout'])
    else:
        print("\n❌ Task timeout")

def test_concurrent_tasks():
    """Test concurrent task execution"""
    print("\n=== Test 3: Concurrent Tasks ===")
    
    code = """
import time
import os

pid = os.getpid()
start = time.time()

# Fibonacci calculation
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

result = fib(35)
end = time.time()

print(f"PID {pid}: fib(35) = {result}, time = {end - start:.2f}s")
"""
    
    print("Submitting 3 concurrent tasks...")
    task_ids = []
    for i in range(3):
        result = submit_task(RAILWAY_URL, code)
        task_ids.append(result['id'])
        print(f"Task {i+1}: {result['id']}")
    
    print("\nWaiting for all tasks to complete...")
    for i, task_id in enumerate(task_ids):
        result = get_task_result(RAILWAY_URL, task_id)
        if result:
            print(f"\n✅ Task {i+1} completed:")
            print(result['result']['stdout'])

def check_worker_stats():
    """Check worker statistics"""
    print("\n=== Worker Statistics ===")
    
    for name, url in [("Railway", RAILWAY_URL), ("Koyeb", KOYEB_URL)]:
        print(f"\n{name} Worker:")
        response = requests.get(f"{url}/stats")
        stats = response.json()
        
        print(f"  Uptime: {stats['monitoring']['uptime_seconds']}s")
        print(f"  Tasks completed: {stats['tasks_completed']}")
        print(f"  Tasks failed: {stats['tasks_failed']}")
        print(f"  CPU: avg={stats['monitoring']['cpu']['avg']}%, max={stats['monitoring']['cpu']['max']}%")
        print(f"  Memory: avg={stats['monitoring']['memory']['avg_mb']:.2f}MB, max={stats['monitoring']['memory']['max_mb']:.2f}MB")

if __name__ == "__main__":
    print("=" * 60)
    print("Worker Performance Test")
    print("=" * 60)
    
    try:
        test_cpu_intensive()
        time.sleep(2)
        
        test_memory_intensive()
        time.sleep(2)
        
        test_concurrent_tasks()
        time.sleep(2)
        
        check_worker_stats()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
