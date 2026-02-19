#!/usr/bin/env python3
"""
Performance stress test for distributed AI workers
"""
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

RAILWAY_URL = "https://lightweight-distributed-ai-production.up.railway.app"
KOYEB_URL = "https://naughty-carina-risker666-8ce36d54.koyeb.app"

def create_task(worker_url, task_type, payload, task_id):
    """Create a single task"""
    start = time.time()
    try:
        response = requests.post(
            f"{worker_url}/tasks",
            json={"type": task_type, "payload": payload},
            timeout=10
        )
        elapsed = time.time() - start
        return {
            'task_id': task_id,
            'worker': worker_url,
            'status': 'success' if response.status_code == 201 else 'failed',
            'response_time': elapsed,
            'result': response.json() if response.status_code == 201 else None
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'task_id': task_id,
            'worker': worker_url,
            'status': 'error',
            'response_time': elapsed,
            'error': str(e)
        }

def stress_test(num_tasks=100, workers=2):
    """Run stress test"""
    print(f"🔥 Starting stress test: {num_tasks} tasks across {workers} workers")
    print("=" * 60)
    
    workers_list = [RAILWAY_URL, KOYEB_URL][:workers]
    
    # Create tasks
    tasks = []
    for i in range(num_tasks):
        worker = workers_list[i % len(workers_list)]
        task_type = ['compute', 'echo'][i % 2]
        
        if task_type == 'compute':
            payload = {
                'operation': ['factorial', 'multiply', 'add'][i % 3],
                'number': 10 + (i % 10),
                'numbers': [i, i+1, i+2]
            }
        else:
            payload = {'message': f'Task {i}'}
        
        tasks.append((worker, task_type, payload, i))
    
    # Execute in parallel
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(create_task, *task) for task in tasks]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if len(results) % 10 == 0:
                print(f"Progress: {len(results)}/{num_tasks} tasks submitted")
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    min_response_time = min(r['response_time'] for r in results)
    max_response_time = max(r['response_time'] for r in results)
    
    print("\n" + "=" * 60)
    print("📊 STRESS TEST RESULTS")
    print("=" * 60)
    print(f"Total tasks: {num_tasks}")
    print(f"Successful: {len(successful)} ({len(successful)/num_tasks*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/num_tasks*100:.1f}%)")
    print(f"Total time: {total_time:.2f}s")
    print(f"Tasks/second: {num_tasks/total_time:.2f}")
    print(f"\nResponse times:")
    print(f"  Average: {avg_response_time:.3f}s")
    print(f"  Min: {min_response_time:.3f}s")
    print(f"  Max: {max_response_time:.3f}s")
    
    # Per-worker stats
    print(f"\n📈 Per-worker statistics:")
    for worker_url in workers_list:
        worker_results = [r for r in results if r['worker'] == worker_url]
        worker_success = [r for r in worker_results if r['status'] == 'success']
        print(f"\n{worker_url.split('//')[1].split('.')[0]}:")
        print(f"  Tasks: {len(worker_results)}")
        print(f"  Success: {len(worker_success)}")
        print(f"  Success rate: {len(worker_success)/len(worker_results)*100:.1f}%")
    
    return results

if __name__ == '__main__':
    # Test 1: 100 tasks
    print("\n🧪 TEST 1: 100 concurrent tasks\n")
    results_100 = stress_test(100, 2)
    
    time.sleep(5)
    
    # Test 2: 500 tasks
    print("\n\n🧪 TEST 2: 500 concurrent tasks\n")
    results_500 = stress_test(500, 2)
    
    print("\n✅ All stress tests completed!")
