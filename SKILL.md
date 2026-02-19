---
name: distributed-exec
description: "Execute code on distributed workers (Railway/Koyeb). Supports Python, JavaScript, and Bash."
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      bins: ["python3"]
---

# Distributed Execution Skill

Execute code on distributed cloud workers from your local OpenClaw agent.

## Quick Start

```bash
# Python execution
python3 /root/.openclaw/workspace/distributed-ai-assistant-project/agent_integration.py

# Or use directly in Python
from agent_integration import run_python, run_javascript, run_bash

result = run_python("print('Hello from cloud!')")
```

## Usage from OpenClaw Agent

When the user asks to run code on distributed workers, use the agent_integration module:

### Example 1: Run Python code

```python
import sys
sys.path.append('/root/.openclaw/workspace/distributed-ai-assistant-project')
from agent_integration import run_python

result = run_python("""
import math
print(f"Pi: {math.pi}")
print(f"E: {math.e}")
""")

if result.get('success'):
    print(result['result']['stdout'])
```

### Example 2: Run JavaScript code

```python
from agent_integration import run_javascript

result = run_javascript("""
const data = [1, 2, 3, 4, 5];
const sum = data.reduce((a, b) => a + b, 0);
console.log('Sum:', sum);
""")
```

### Example 3: Complex algorithm execution

```python
from agent_integration import run_python

# 在云端执行复杂算法
code = '''
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
print(f"Sorted: {quicksort(data)}")
'''

result = run_python(code)
print(result['result']['stdout'])
```

## API Reference

### DistributedWorkerClient

Main client class for interacting with workers.

**Methods:**
- `execute_code(language, code, worker_url=None, timeout=60)` - Execute code
- `execute_python(code, **kwargs)` - Execute Python
- `execute_javascript(code, **kwargs)` - Execute JavaScript
- `execute_bash(code, **kwargs)` - Execute Bash
- `list_workers()` - List all workers
- `get_worker_stats(worker_url)` - Get worker statistics

### Convenience Functions

- `run_python(code, **kwargs)` - Quick Python execution
- `run_javascript(code, **kwargs)` - Quick JavaScript execution
- `run_bash(code, **kwargs)` - Quick Bash execution

## Return Format

```python
{
    "success": True,
    "task_id": "task-id-here",
    "worker": "https://worker-url",
    "result": {
        "stdout": "output here",
        "stderr": "",
        "returncode": 0,
        "success": True
    },
    "execution_time": 1.23
}
```

## Use Cases

1. **Heavy Computation** - Offload CPU-intensive tasks to cloud workers
2. **Parallel Execution** - Run multiple tasks simultaneously
3. **Testing** - Test code in isolated environments
4. **Data Processing** - Process large datasets in the cloud
5. **Algorithm Verification** - Verify algorithms before local execution

## Workers

Current active workers:
- Railway: https://lightweight-distributed-ai-production.up.railway.app
- Koyeb: https://naughty-carina-risker666-8ce36d54.koyeb.app

## Performance

- Typical execution time: 1-3 seconds
- Timeout: 60 seconds (configurable)
- Success rate: 100%
- Memory per worker: ~34MB

## Examples

See `agent_integration.py` for complete examples and test code.
