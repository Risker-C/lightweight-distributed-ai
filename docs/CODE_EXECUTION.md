# 代码执行功能文档

## 支持的语言

- **Python 3** - 数据处理、算法、AI/ML
- **JavaScript (Node.js)** - Web开发、异步操作
- **Bash** - 系统管理、自动化脚本

## API 使用

### 提交代码执行任务

```bash
curl -X POST https://YOUR_WORKER_URL/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "code",
    "payload": {
      "language": "python",
      "code": "print(\"Hello, World!\")"
    }
  }'
```

### 响应示例

```json
{
  "id": "task-id-here",
  "status": "pending",
  "message": "Task queued successfully"
}
```

### 查询任务结果

```bash
curl https://YOUR_WORKER_URL/tasks/task-id-here
```

### 结果示例

```json
{
  "id": "task-id-here",
  "status": "completed",
  "result": {
    "stdout": "Hello, World!\n",
    "stderr": "",
    "returncode": 0,
    "success": true
  }
}
```

## 示例任务

### 1. Python - 数据分析

```python
{
  "type": "code",
  "payload": {
    "language": "python",
    "code": """
import statistics

data = [10, 20, 30, 40, 50]
print(f"Mean: {statistics.mean(data)}")
print(f"Median: {statistics.median(data)}")
print(f"Std Dev: {statistics.stdev(data):.2f}")
"""
  }
}
```

### 2. JavaScript - 算法

```javascript
{
  "type": "code",
  "payload": {
    "language": "javascript",
    "code": "const factorial = n => n <= 1 ? 1 : n * factorial(n - 1);\nconsole.log('10! =', factorial(10));"
  }
}
```

### 3. Bash - 系统操作

```bash
{
  "type": "code",
  "payload": {
    "language": "bash",
    "code": "echo 'System: '$(uname -s)\necho 'Python: '$(python3 --version)"
  }
}
```

## 复杂任务示例

### 机器学习数据预处理

```python
{
  "type": "code",
  "payload": {
    "language": "python",
    "code": """
import json

# 模拟数据集
data = [
    {"feature1": 1.2, "feature2": 3.4, "label": 0},
    {"feature1": 2.3, "feature2": 4.5, "label": 1},
    {"feature1": 3.4, "feature2": 5.6, "label": 0}
]

# 归一化
max_f1 = max(d['feature1'] for d in data)
max_f2 = max(d['feature2'] for d in data)

normalized = [
    {
        'feature1': d['feature1'] / max_f1,
        'feature2': d['feature2'] / max_f2,
        'label': d['label']
    }
    for d in data
]

print(json.dumps(normalized, indent=2))
"""
  }
}
```

### Web数据爬取模拟

```python
{
  "type": "code",
  "payload": {
    "language": "python",
    "code": """
import re
import json

# 模拟HTML内容
html = '''
<div class="product">
  <h2>Product A</h2>
  <span class="price">$29.99</span>
</div>
<div class="product">
  <h2>Product B</h2>
  <span class="price">$49.99</span>
</div>
'''

# 提取产品信息
products = []
for match in re.finditer(r'<h2>(.*?)</h2>.*?<span class="price">(.*?)</span>', html, re.DOTALL):
    products.append({
        'name': match.group(1),
        'price': match.group(2)
    })

print(json.dumps(products, indent=2))
"""
  }
}
```

## 安全限制

- **执行超时**: 30秒
- **内存限制**: Worker内存限制
- **文件系统**: 仅临时文件访问
- **网络**: 取决于Worker环境配置

## 性能

- **启动时间**: <100ms
- **执行开销**: 最小
- **并发**: 支持多任务并行

## 使用场景

1. **数据处理**: CSV/JSON解析和转换
2. **算法验证**: 快速测试算法实现
3. **自动化任务**: 定时脚本执行
4. **API集成**: 调用外部服务
5. **报表生成**: 数据分析和可视化
6. **测试运行**: 单元测试和集成测试

## 最佳实践

1. **代码简洁**: 保持任务代码简短高效
2. **错误处理**: 包含适当的异常处理
3. **日志输出**: 使用print/console.log输出调试信息
4. **超时考虑**: 长时间任务应分解为多个子任务
5. **资源管理**: 避免内存泄漏和资源占用

## 扩展支持

未来计划支持：
- Go语言
- Rust
- Ruby
- PHP
- C/C++ (编译执行)

---

**版本**: v2.1.0  
**最后更新**: 2026-02-19
