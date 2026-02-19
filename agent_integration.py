#!/usr/bin/env python3
"""
Agent Integration Module - 让OpenClaw Agent接管Worker执行编程任务
"""
import requests
import json
import time
from typing import Dict, Any, Optional

class DistributedWorkerClient:
    """分布式Worker客户端 - 供OpenClaw Agent使用"""
    
    def __init__(self, root_node_url="http://localhost:5000"):
        self.root_node_url = root_node_url
        self.workers = []
        self.refresh_workers()
    
    def refresh_workers(self):
        """刷新Worker列表"""
        try:
            response = requests.get(f"{self.root_node_url}/workers", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.workers = data.get('workers', [])
                return True
        except Exception as e:
            print(f"Failed to refresh workers: {e}")
        return False
    
    def execute_code(self, language: str, code: str, 
                    worker_url: Optional[str] = None,
                    timeout: int = 60) -> Dict[str, Any]:
        """
        在Worker上执行代码
        
        Args:
            language: 编程语言 (python, javascript, bash)
            code: 代码内容
            worker_url: 指定Worker URL（可选，默认自动选择）
            timeout: 超时时间（秒）
        
        Returns:
            执行结果字典
        """
        # 选择Worker
        if worker_url is None:
            if not self.workers:
                self.refresh_workers()
            if not self.workers:
                return {"error": "No workers available"}
            
            # 选择在线的Worker
            online_workers = [w for w in self.workers if w.get('status') == 'online']
            if not online_workers:
                return {"error": "No online workers"}
            
            worker_url = online_workers[0]['url']
        
        # 提交任务
        try:
            task_data = {
                "type": "code",
                "payload": {
                    "language": language,
                    "code": code
                }
            }
            
            response = requests.post(
                f"{worker_url}/tasks",
                json=task_data,
                timeout=10
            )
            
            if response.status_code != 201:
                return {"error": f"Failed to create task: {response.text}"}
            
            task_id = response.json()['id']
            
            # 轮询结果
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(1)
                
                result_response = requests.get(
                    f"{worker_url}/tasks/{task_id}",
                    timeout=10
                )
                
                if result_response.status_code != 200:
                    continue
                
                result = result_response.json()
                
                if result['status'] == 'completed':
                    return {
                        "success": True,
                        "task_id": task_id,
                        "worker": worker_url,
                        "result": result['result'],
                        "execution_time": time.time() - start_time
                    }
                elif result['status'] == 'failed':
                    return {
                        "success": False,
                        "task_id": task_id,
                        "error": result.get('error', 'Unknown error')
                    }
            
            return {"error": f"Timeout after {timeout}s"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def execute_python(self, code: str, **kwargs) -> Dict[str, Any]:
        """执行Python代码"""
        return self.execute_code("python", code, **kwargs)
    
    def execute_javascript(self, code: str, **kwargs) -> Dict[str, Any]:
        """执行JavaScript代码"""
        return self.execute_code("javascript", code, **kwargs)
    
    def execute_bash(self, code: str, **kwargs) -> Dict[str, Any]:
        """执行Bash脚本"""
        return self.execute_code("bash", code, **kwargs)
    
    def get_worker_stats(self, worker_url: str) -> Dict[str, Any]:
        """获取Worker统计信息"""
        try:
            response = requests.get(f"{worker_url}/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"error": str(e)}
        return {}
    
    def list_workers(self) -> list:
        """列出所有Worker"""
        self.refresh_workers()
        return self.workers


# 全局客户端实例
_client = None

def get_client(root_node_url="http://localhost:5000"):
    """获取全局客户端实例"""
    global _client
    if _client is None:
        _client = DistributedWorkerClient(root_node_url)
    return _client


# 便捷函数
def run_python(code: str, **kwargs):
    """在分布式Worker上运行Python代码"""
    client = get_client()
    return client.execute_python(code, **kwargs)

def run_javascript(code: str, **kwargs):
    """在分布式Worker上运行JavaScript代码"""
    client = get_client()
    return client.execute_javascript(code, **kwargs)

def run_bash(code: str, **kwargs):
    """在分布式Worker上运行Bash脚本"""
    client = get_client()
    return client.execute_bash(code, **kwargs)


if __name__ == "__main__":
    # 测试示例
    print("=== Distributed Worker Client Test ===\n")
    
    client = get_client()
    
    # 列出Workers
    print("Available workers:")
    workers = client.list_workers()
    for w in workers:
        print(f"  - {w['name']}: {w['url']} ({w['status']})")
    
    # 测试Python执行
    print("\n--- Python Test ---")
    result = run_python("""
print("Hello from distributed worker!")
import sys
print(f"Python version: {sys.version}")
result = sum(range(100))
print(f"Sum of 0-99: {result}")
""")
    
    if result.get('success'):
        print(f"✓ Success (took {result['execution_time']:.2f}s)")
        print(f"Output:\n{result['result']['stdout']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
    
    # 测试JavaScript执行
    print("\n--- JavaScript Test ---")
    result = run_javascript("""
console.log("Hello from Node.js worker!");
console.log("Node version:", process.version);
const sum = Array.from({length: 100}, (_, i) => i).reduce((a, b) => a + b, 0);
console.log("Sum of 0-99:", sum);
""")
    
    if result.get('success'):
        print(f"✓ Success (took {result['execution_time']:.2f}s)")
        print(f"Output:\n{result['result']['stdout']}")
    else:
        print(f"✗ Failed: {result.get('error')}")
