# JARVIS Metrics Reference

## 📊 Complete Metrics Catalog

### System Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_cpu_usage_percent` | Gauge | CPU usage percentage | - |
| `jarvis_memory_usage_bytes` | Gauge | Memory usage in bytes | - |
| `jarvis_memory_usage_percent` | Gauge | Memory usage percentage | - |
| `jarvis_disk_usage_percent` | Gauge | Disk usage percentage | - |
| `jarvis_uptime_seconds` | Gauge | System uptime in seconds | - |

### Workflow Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_workflows_total` | Counter | Total workflows executed | `status`, `engine` |
| `jarvis_workflow_duration_seconds` | Histogram | Workflow execution time | `workflow_type` |

### Tool Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_tool_executions_total` | Counter | Total tool executions | `tool_name`, `status` |
| `jarvis_tool_duration_seconds` | Histogram | Tool execution time | `tool_name` |

### LLM Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_llm_requests_total` | Counter | Total LLM requests | `provider`, `model` |
| `jarvis_llm_tokens_total` | Counter | Total tokens used | `provider`, `type` |
| `jarvis_llm_duration_seconds` | Histogram | LLM response time | `provider` |

### Health Metrics

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_health_status` | Gauge | Component health (1=healthy, 0=unhealthy) | `component` |
| `jarvis_errors_total` | Counter | Total errors by component | `component`, `error_type` |

### System Info

| Metric Name | Type | Description | Labels |
|-------------|------|-------------|--------|
| `jarvis_info` | Info | System information | `version`, `python_version`, `platform`, `start_time` |

## 🚨 Alert Rules Reference

### Critical Alerts

#### High CPU Usage
```yaml
alert: HighCPUUsage
expr: jarvis_cpu_usage_percent > 80
for: 5m
labels:
  severity: warning
annotations:
  summary: "High CPU usage detected"
  description: "CPU usage is {{ $value }}% for more than 5 minutes"
```

#### High Memory Usage
```yaml
alert: HighMemoryUsage
expr: jarvis_memory_usage_percent > 90
for: 5m
labels:
  severity: critical
annotations:
  summary: "High memory usage detected"
  description: "Memory usage is {{ $value }}% for more than 5 minutes"
```

#### Component Down
```yaml
alert: ComponentDown
expr: jarvis_health_status == 0
for: 1m
labels:
  severity: critical
annotations:
  summary: "Component {{ $labels.component }} is down"
  description: "Component {{ $labels.component }} has been unhealthy for more than 1 minute"
```

#### High Error Rate
```yaml
alert: HighErrorRate
expr: rate(jarvis_errors_total[5m]) > 0.1
for: 2m
labels:
  severity: warning
annotations:
  summary: "High error rate in {{ $labels.component }}"
  description: "Error rate is {{ $value }} errors/second in {{ $labels.component }}"
```

### Performance Alerts

#### Slow Workflows
```yaml
alert: SlowWorkflows
expr: histogram_quantile(0.95, jarvis_workflow_duration_seconds) > 30
for: 5m
labels:
  severity: warning
annotations:
  summary: "Workflows are running slowly"
  description: "95th percentile workflow duration is {{ $value }} seconds"
```

#### LLM Timeout
```yaml
alert: LLMTimeout
expr: histogram_quantile(0.95, jarvis_llm_duration_seconds) > 10
for: 3m
labels:
  severity: warning
annotations:
  summary: "LLM responses are slow"
  description: "95th percentile LLM response time is {{ $value }} seconds"
```

## 📈 Dashboard Queries

### System Overview Queries

#### CPU Usage Over Time
```promql
jarvis_cpu_usage_percent
```

#### Memory Usage Trend
```promql
jarvis_memory_usage_percent
```

#### Disk Space Remaining
```promql
100 - jarvis_disk_usage_percent
```

### Performance Queries

#### Workflow Success Rate (Last Hour)
```promql
rate(jarvis_workflows_total{status="success"}[1h]) / rate(jarvis_workflows_total[1h]) * 100
```

#### Average Workflow Duration
```promql
rate(jarvis_workflow_duration_seconds_sum[5m]) / rate(jarvis_workflow_duration_seconds_count[5m])
```

#### Top 5 Most Used Tools
```promql
topk(5, sum by (tool_name) (jarvis_tool_executions_total))
```

#### LLM Token Usage by Provider
```promql
sum by (provider) (rate(jarvis_llm_tokens_total[1h]))
```

### Health Queries

#### Healthy Components Count
```promql
sum(jarvis_health_status)
```

#### Error Rate by Component
```promql
sum by (component) (rate(jarvis_errors_total[5m]))
```

#### System Uptime in Days
```promql
jarvis_uptime_seconds / 86400
```

## 🎯 Metric Collection Intervals

| Metric Category | Collection Interval | Retention |
|-----------------|-------------------|-----------|
| System Metrics | 30 seconds | 7 days |
| Workflow Metrics | On execution | 30 days |
| Tool Metrics | On execution | 30 days |
| LLM Metrics | On request | 30 days |
| Health Checks | 60 seconds | 7 days |
| Error Metrics | On error | 30 days |

## 🔧 Custom Metrics

### Adding New Metrics

To add custom metrics to JARVIS:

1. **Import metrics in your code:**
```python
from core.monitoring.metrics import jarvis_metrics
```

2. **Record metrics:**
```python
# Record workflow execution
jarvis_metrics.record_workflow_execution(
    workflow_type="custom_workflow",
    duration=2.5,
    status="success",
    engine="temporal"
)

# Record tool execution
jarvis_metrics.record_tool_execution(
    tool_name="custom_tool",
    duration=1.2,
    status="success"
)

# Record custom error
jarvis_metrics.record_error(
    component="custom_component",
    error_type="validation_error"
)
```

3. **Set health status:**
```python
jarvis_metrics.set_health_status("custom_component", True)
```

### Metric Naming Conventions

- Use `jarvis_` prefix for all metrics
- Use snake_case for metric names
- Include units in metric names (e.g., `_seconds`, `_bytes`, `_percent`)
- Use descriptive labels for categorization

---
*For implementation details, see monitoring/monitoring_guide.md*
