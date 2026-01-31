# JARVIS Development Guide - Building & Extending the System

## 🎯 Development Philosophy

JARVIS is built with these core principles:
- **Modularity**: Each component is independent and replaceable
- **Extensibility**: Easy to add new tools, skills, and workflows
- **Maintainability**: Clean code, clear interfaces, comprehensive testing
- **Scalability**: Designed to handle increasing complexity and load

## 🚀 Getting Started with Development

### Development Environment Setup

1. **Clone and Setup**
```bash
git clone <jarvis-repo>
cd jarvis
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. **Configuration**
```bash
# Create development environment
python config_cli.py create-env
export JARVIS_ENV=development

# Set up monitoring (optional)
docker-compose -f docker-compose-monitoring.yml up -d
```

3. **Verify Installation**
```bash
python config_cli.py test
python -c "from core.config.config_manager import config_manager; print('✅ JARVIS ready')"
```

## 🔧 Adding New Tools

### Tool Development Pattern

1. **Create Tool Class**
```python
# modules/tools/my_custom_tool.py
from .base_tool import BaseTool, ToolResult

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Description of what this tool does",
            parameters={
                "param1": {"type": "string", "required": True, "description": "Parameter description"},
                "param2": {"type": "integer", "required": False, "default": 10}
            }
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            # Tool implementation
            param1 = kwargs.get("param1")
            param2 = kwargs.get("param2", 10)
            
            # Your tool logic here
            result = f"Processed {param1} with value {param2}"
            
            return ToolResult(
                success=True,
                output=result,
                metadata={"execution_time": 0.5}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=str(e)
            )
```

2. **Register Tool**
```python
# In your initialization code or main.py
from modules.tools.my_custom_tool import MyCustomTool
from modules.tools.base_tool import tool_registry

# Register the tool
tool_registry.register_tool(MyCustomTool())
```

3. **Test Tool**
```python
# test_my_custom_tool.py
import asyncio
from modules.tools.base_tool import tool_registry

async def test_custom_tool():
    result = await tool_registry.execute_tool(
        "my_custom_tool",
        param1="test_value",
        param2=20
    )
    print(f"Result: {result.output}")

asyncio.run(test_custom_tool())
```

## 🧠 Creating Custom Skills

### Skill Development Pattern

1. **Define Skill Class**
```python
# skills/my_custom_skill.py
from .skill_framework import BaseSkill, SkillResult

class MyCustomSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="my_custom_skill",
            description="Custom skill for specific domain",
            domain="custom_domain"
        )
    
    def can_handle(self, task_description: str) -> float:
        """Return confidence score (0-1) for handling this task"""
        if "custom_keyword" in task_description.lower():
            return 0.9
        return 0.0
    
    async def execute_skill(self, task_description: str, context: dict) -> SkillResult:
        """Execute the skill logic"""
        try:
            # Skill implementation
            steps = self.plan_execution(task_description)
            results = []
            
            for step in steps:
                result = await self.execute_step(step, context)
                results.append(result)
            
            return SkillResult(
                success=True,
                output=results,
                confidence=0.9,
                metadata={"steps_executed": len(steps)}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error_message=str(e)
            )
    
    def plan_execution(self, task_description: str) -> list:
        """Break down task into executable steps"""
        # Your planning logic here
        return ["step1", "step2", "step3"]
    
    async def execute_step(self, step: str, context: dict):
        """Execute individual step"""
        # Your step execution logic here
        return f"Executed {step}"
```

## 🔄 Building Custom Workflows

### Simple Workflow Pattern

1. **Define Workflow**
```python
# workflows/custom/my_workflow.py
from core.engines.workflow.simple_workflow import SimpleWorkflow, WorkflowStep

def create_custom_workflow(input_data: dict) -> SimpleWorkflow:
    """Create a custom workflow"""
    
    steps = [
        WorkflowStep(
            id="step1",
            name="Data Processing",
            tool="my_custom_tool",
            parameters={"param1": input_data.get("input_value")}
        ),
        WorkflowStep(
            id="step2",
            name="Result Analysis",
            tool="calculator",
            parameters={"expression": "2 + 2"},
            depends_on=["step1"]
        )
    ]
    
    return SimpleWorkflow(
        id=f"custom_workflow_{int(time.time())}",
        name="My Custom Workflow",
        steps=steps
    )
```

### Temporal Workflow Pattern

1. **Define Temporal Workflow**
```python
# core/workflows/custom_temporal_workflow.py
from temporalio import workflow, activity
from datetime import timedelta

@workflow.defn
class MyCustomWorkflow:
    @workflow.run
    async def run(self, input_data: dict) -> dict:
        # Step 1: Process data
        result1 = await workflow.execute_activity(
            process_data_activity,
            input_data,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Step 2: Analyze results
        result2 = await workflow.execute_activity(
            analyze_results_activity,
            result1,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        return {
            "workflow_id": workflow.info().workflow_id,
            "results": [result1, result2]
        }

@activity.defn
async def process_data_activity(data: dict) -> dict:
    # Your data processing logic
    return {"processed": True, "data": data}

@activity.defn
async def analyze_results_activity(results: dict) -> dict:
    # Your analysis logic
    return {"analysis": "completed", "insights": ["insight1", "insight2"]}
```

## 📊 Adding Custom Metrics

### Metrics Integration

1. **Define Custom Metrics**
```python
# core/monitoring/custom_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define your custom metrics
custom_operations_total = Counter(
    'jarvis_custom_operations_total',
    'Total custom operations',
    ['operation_type', 'status']
)

custom_operation_duration = Histogram(
    'jarvis_custom_operation_duration_seconds',
    'Custom operation duration',
    ['operation_type']
)

custom_queue_size = Gauge(
    'jarvis_custom_queue_size',
    'Current custom queue size'
)
```

2. **Record Metrics**
```python
# In your custom tool or skill
from core.monitoring.custom_metrics import custom_operations_total, custom_operation_duration
import time

class MyCustomTool(BaseTool):
    async def execute(self, **kwargs) -> ToolResult:
        start_time = time.time()
        
        try:
            # Your tool logic
            result = self.do_work(kwargs)
            
            # Record success metric
            custom_operations_total.labels(
                operation_type="my_operation",
                status="success"
            ).inc()
            
            return ToolResult(success=True, output=result)
            
        except Exception as e:
            # Record failure metric
            custom_operations_total.labels(
                operation_type="my_operation",
                status="failure"
            ).inc()
            
            return ToolResult(success=False, error_message=str(e))
            
        finally:
            # Record duration
            duration = time.time() - start_time
            custom_operation_duration.labels(
                operation_type="my_operation"
            ).observe(duration)
```

## 🔧 Configuration Extensions

### Adding New Configuration Sections

1. **Extend Configuration Schema**
```python
# core/config/config_manager.py - Add to JarvisConfig dataclass
@dataclass
class JarvisConfig:
    # ... existing fields ...
    
    # New custom section
    custom_service_enabled: bool
    custom_service_url: str
    custom_service_timeout: int
```

2. **Update Environment Files**
```yaml
# config/environments/development.yaml
custom_service:
  enabled: true
  url: "http://localhost:8000"
  timeout: 30
```

3. **Update Config Loading**
```python
# In config_manager.py load_config method
self.config = JarvisConfig(
    # ... existing fields ...
    
    # New custom fields
    custom_service_enabled=config_data["custom_service"]["enabled"],
    custom_service_url=config_data["custom_service"]["url"],
    custom_service_timeout=config_data["custom_service"]["timeout"]
)
```

## 🧪 Testing Strategies

### Unit Testing Pattern

1. **Tool Testing**
```python
# tests/test_my_custom_tool.py
import pytest
import asyncio
from modules.tools.my_custom_tool import MyCustomTool

class TestMyCustomTool:
    def setup_method(self):
        self.tool = MyCustomTool()
    
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        result = await self.tool.execute(param1="test", param2=10)
        assert result.success is True
        assert "test" in result.output
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        result = await self.tool.execute()  # Missing required param
        assert result.success is False
        assert result.error_message is not None
```

### Integration Testing Pattern

1. **Workflow Testing**
```python
# tests/test_custom_workflow.py
import pytest
from core.engines.workflow.enhanced_workflow import enhanced_workflow_engine, EnhancedWorkflowRequest

class TestCustomWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        request = EnhancedWorkflowRequest(
            name="Test Custom Workflow",
            description="Testing custom workflow",
            workflow_type="simple",
            parameters={"input_value": "test_data"}
        )
        
        result = await enhanced_workflow_engine.execute_workflow(request)
        assert result["success"] is True
```

## 🚀 Performance Optimization

### Optimization Strategies

1. **Caching Implementation**
```python
# utils/cache.py
from functools import lru_cache
import asyncio

class AsyncLRUCache:
    def __init__(self, maxsize=128):
        self.cache = {}
        self.maxsize = maxsize
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in self.cache:
                return self.cache[key]
            
            result = await func(*args, **kwargs)
            
            if len(self.cache) >= self.maxsize:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[key] = result
            return result
        
        return wrapper

# Usage in tools
@AsyncLRUCache(maxsize=100)
async def expensive_operation(param):
    # Expensive computation
    await asyncio.sleep(1)
    return f"Result for {param}"
```

2. **Async Optimization**
```python
# Parallel execution pattern
async def execute_parallel_tasks(tasks):
    """Execute multiple tasks in parallel"""
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful_results = []
    errors = []
    
    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
        else:
            successful_results.append(result)
    
    return successful_results, errors
```

## 🔐 Security Best Practices

### Security Implementation

1. **Input Validation**
```python
# utils/security.py
import re
from typing import Any, Dict

class SecurityValidator:
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf',
        r'sudo\s+',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__'
    ]
    
    @classmethod
    def validate_command(cls, command: str) -> bool:
        """Validate shell command for security"""
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        return True
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[;&|`$]', '', user_input)
        return sanitized.strip()
```

2. **Permission Management**
```python
# core/security/permissions.py
from enum import Enum
from typing import Set

class Permission(Enum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_COMMANDS = "execute_commands"
    NETWORK_ACCESS = "network_access"

class PermissionManager:
    def __init__(self):
        self.tool_permissions: Dict[str, Set[Permission]] = {}
    
    def grant_permission(self, tool_name: str, permission: Permission):
        if tool_name not in self.tool_permissions:
            self.tool_permissions[tool_name] = set()
        self.tool_permissions[tool_name].add(permission)
    
    def check_permission(self, tool_name: str, permission: Permission) -> bool:
        return permission in self.tool_permissions.get(tool_name, set())
```

## 📈 Monitoring & Observability

### Custom Dashboard Creation

1. **Grafana Dashboard JSON**
```json
{
  "dashboard": {
    "title": "Custom JARVIS Dashboard",
    "panels": [
      {
        "title": "Custom Operations Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(jarvis_custom_operations_total[5m])",
            "legendFormat": "{{operation_type}}"
          }
        ]
      }
    ]
  }
}
```

2. **Custom Health Checks**
```python
# core/monitoring/custom_health.py
from core.monitoring.metrics import health_checker

async def custom_service_health_check() -> bool:
    """Custom health check for your service"""
    try:
        # Check your service health
        response = await check_service_status()
        return response.status_code == 200
    except Exception:
        return False

# Register health check
health_checker.register_component("custom_service", custom_service_health_check)
```

## 🎯 Deployment Strategies

### Production Deployment

1. **Docker Configuration**
```dockerfile
# Dockerfile.jarvis
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9090
CMD ["python", "main.py"]
```

2. **Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  jarvis:
    build: .
    environment:
      - JARVIS_ENV=production
      - LLM_API_KEY=${LLM_API_KEY}
    ports:
      - "9090:9090"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## 🔄 Continuous Integration

### CI/CD Pipeline

1. **GitHub Actions Example**
```yaml
# .github/workflows/ci.yml
name: JARVIS CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/
      - name: Run linting
        run: flake8 .
```

---

*This development guide provides the foundation for extending JARVIS with new capabilities while maintaining code quality, security, and performance standards.*
