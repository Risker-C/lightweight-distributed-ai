#!/usr/bin/env python3
"""
Test complex programming tasks on distributed workers
"""
import requests
import json
import time

RAILWAY_URL = "https://lightweight-distributed-ai-production.up.railway.app"
KOYEB_URL = "https://naughty-carina-risker666-8ce36d54.koyeb.app"

def test_code_execution(worker_url, test_name, language, code, input_data=None):
    """Test code execution"""
    print(f"\n{'='*60}")
    print(f"🧪 Test: {test_name}")
    print(f"Worker: {worker_url.split('//')[1].split('.')[0]}")
    print(f"Language: {language}")
    print(f"{'='*60}")
    
    # Create task
    task_data = {
        "type": "code",
        "payload": {
            "language": language,
            "code": code
        }
    }
    if input_data:
        task_data["payload"]["input"] = input_data
    
    start = time.time()
    response = requests.post(f"{worker_url}/tasks", json=task_data, timeout=30)
    
    if response.status_code != 201:
        print(f"❌ Failed to create task: {response.text}")
        return
    
    task_id = response.json()['id']
    print(f"📝 Task ID: {task_id}")
    
    # Poll for result
    max_wait = 30
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(1)
        elapsed = time.time() - start
        
        result_response = requests.get(f"{worker_url}/tasks/{task_id}", timeout=10)
        if result_response.status_code != 200:
            continue
        
        result = result_response.json()
        if result['status'] == 'completed':
            print(f"✅ Completed in {elapsed:.2f}s")
            print(f"\n📤 Output:")
            print(result['result'].get('output', ''))
            if result['result'].get('error'):
                print(f"\n⚠️  Errors:")
                print(result['result']['error'])
            return result
        elif result['status'] == 'failed':
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return result
    
    print(f"⏱️  Timeout after {max_wait}s")

# Test cases
print("🚀 Starting Complex Programming Task Tests")
print("="*60)

# Test 1: Python - Fibonacci sequence
test_code_execution(
    RAILWAY_URL,
    "Python: Fibonacci Sequence",
    "python",
    """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

for i in range(15):
    print(f"fib({i}) = {fibonacci(i)}")
"""
)

# Test 2: Python - Prime numbers
test_code_execution(
    KOYEB_URL,
    "Python: Prime Numbers",
    "python",
    """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [n for n in range(2, 100) if is_prime(n)]
print(f"Primes under 100: {primes}")
print(f"Total: {len(primes)} primes")
"""
)

# Test 3: JavaScript - Array operations
test_code_execution(
    RAILWAY_URL,
    "JavaScript: Array Operations",
    "javascript",
    """
const numbers = Array.from({length: 20}, (_, i) => i + 1);

const squares = numbers.map(n => n * n);
const sum = squares.reduce((a, b) => a + b, 0);
const avg = sum / squares.length;

console.log('Numbers:', numbers);
console.log('Squares:', squares);
console.log('Sum:', sum);
console.log('Average:', avg);
"""
)

# Test 4: Python - Data processing
test_code_execution(
    KOYEB_URL,
    "Python: Data Processing",
    "python",
    """
import json

data = [
    {"name": "Alice", "age": 30, "score": 95},
    {"name": "Bob", "age": 25, "score": 87},
    {"name": "Charlie", "age": 35, "score": 92},
    {"name": "David", "age": 28, "score": 88}
]

# Sort by score
sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)

print("Top performers:")
for i, person in enumerate(sorted_data, 1):
    print(f"{i}. {person['name']}: {person['score']} points")

avg_score = sum(p['score'] for p in data) / len(data)
print(f"\\nAverage score: {avg_score:.2f}")
"""
)

# Test 5: Bash - System info
test_code_execution(
    RAILWAY_URL,
    "Bash: System Information",
    "bash",
    """
echo "=== System Information ==="
echo "Date: $(date)"
echo "Uptime: $(uptime -p 2>/dev/null || echo 'N/A')"
echo "Python version: $(python3 --version)"
echo "Node version: $(node --version 2>/dev/null || echo 'Not installed')"
echo ""
echo "=== Environment ==="
echo "PATH: $PATH"
echo "PWD: $PWD"
"""
)

# Test 6: Python - Algorithm (Sorting)
test_code_execution(
    KOYEB_URL,
    "Python: QuickSort Algorithm",
    "python",
    """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

import random
data = [random.randint(1, 100) for _ in range(20)]
print(f"Original: {data}")
sorted_data = quicksort(data)
print(f"Sorted:   {sorted_data}")
"""
)

# Test 7: JavaScript - Async operations
test_code_execution(
    RAILWAY_URL,
    "JavaScript: Promise Chain",
    "javascript",
    """
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function processData() {
    console.log('Starting...');
    
    await delay(100);
    console.log('Step 1 complete');
    
    await delay(100);
    console.log('Step 2 complete');
    
    await delay(100);
    console.log('Step 3 complete');
    
    return 'All done!';
}

processData().then(result => console.log(result));
"""
)

# Test 8: Python - Web scraping simulation
test_code_execution(
    KOYEB_URL,
    "Python: JSON Processing",
    "python",
    """
import json

# Simulate API response
api_data = '''
{
    "users": [
        {"id": 1, "name": "Alice", "posts": 42},
        {"id": 2, "name": "Bob", "posts": 38},
        {"id": 3, "name": "Charlie", "posts": 55}
    ],
    "total": 3
}
'''

data = json.loads(api_data)

print("User Statistics:")
print("-" * 40)
for user in data['users']:
    print(f"ID: {user['id']:2d} | {user['name']:10s} | Posts: {user['posts']}")

total_posts = sum(u['posts'] for u in data['users'])
print("-" * 40)
print(f"Total posts: {total_posts}")
print(f"Average: {total_posts / data['total']:.1f} posts/user")
"""
)

print("\n" + "="*60)
print("✅ All complex programming tests completed!")
print("="*60)
