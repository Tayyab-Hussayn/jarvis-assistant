# JARVIS Monitoring System - Complete User Guide

## 🎯 Overview

JARVIS includes a comprehensive monitoring stack that tracks system performance, workflow execution, and component health in real-time.

## 🌐 Access Points

### Primary Dashboards

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Grafana** | http://localhost:3000 | admin / jarvis123 | Main monitoring dashboard |
| **Prometheus** | http://localhost:9091 | None | Metrics database & queries |
| **Alertmanager** | http://localhost:9093 | None | Alert management |
| **JARVIS Metrics** | http://localhost:9090/metrics | None | Raw metrics endpoint |

### Additional Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Temporal UI** | http://localhost:8080 | Workflow monitoring |

## 📊 Grafana Dashboard Guide

### Login & Setup
1. Open http://localhost:3000
2. Login: `admin` / `jarvis123`
3. Navigate to dashboards (will be auto-provisioned)

### Key Metrics to Monitor

#### System Health
- **CPU Usage**: Current system CPU utilization
- **Memory Usage**: RAM consumption (bytes & percentage)
- **Disk Usage**: Storage utilization percentage
- **Uptime**: System running time

#### JARVIS Performance
- **Workflow Executions**: Success/failure rates by engine type
- **Tool Usage**: Most used tools and execution times
- **LLM Requests**: API calls, token usage, response times
- **Error Rates**: Component-specific error tracking

#### Component Health
- **Health Status**: Green/red indicators for each component
- **Response Times**: Service latency monitoring
- **Resource Usage**: Per-component resource consumption

## 🔍 Prometheus Query Examples

Access Prometheus at http://localhost:9091 and use these queries:

### System Queries
```promql
# CPU usage percentage
jarvis_cpu_usage_percent

# Memory usage in GB
jarvis_memory_usage_bytes / 1024 / 1024 / 1024

# Disk usage percentage
jarvis_disk_usage_percent
```

### JARVIS Queries
```promql
# Workflow success rate (last hour)
rate(jarvis_workflows_total{status="success"}[1h])

# Most used tools
topk(5, sum by (tool_name) (jarvis_tool_executions_total))

# LLM token usage by provider
sum by (provider) (jarvis_llm_tokens_total)

# Error rate by component
rate(jarvis_errors_total[5m])
```

### Health Queries
```promql
# Unhealthy components
jarvis_health_status == 0

# System uptime in hours
jarvis_uptime_seconds / 3600
```

## 🚨 Alert Configuration

### Default Alerts
- **High CPU Usage**: >80% for 5 minutes
- **High Memory Usage**: >90% for 5 minutes
- **Component Down**: Health status = 0
- **High Error Rate**: >10 errors/minute

### Custom Alerts
Edit `monitoring/prometheus.yml` to add custom alert rules.

## 📈 Understanding Metrics

### Metric Types

#### Counters (Always Increasing)
- `jarvis_workflows_total`: Total workflows executed
- `jarvis_tool_executions_total`: Total tool executions
- `jarvis_llm_requests_total`: Total LLM requests
- `jarvis_errors_total`: Total errors

#### Gauges (Current Values)
- `jarvis_cpu_usage_percent`: Current CPU usage
- `jarvis_memory_usage_bytes`: Current memory usage
- `jarvis_health_status`: Component health (1=healthy, 0=unhealthy)

#### Histograms (Distribution)
- `jarvis_workflow_duration_seconds`: Workflow execution times
- `jarvis_tool_duration_seconds`: Tool execution times
- `jarvis_llm_duration_seconds`: LLM response times

## 🔧 Management Commands

### Start/Stop Monitoring
```bash
# Start monitoring stack
docker-compose -f docker-compose-monitoring.yml up -d

# Stop monitoring stack
docker-compose -f docker-compose-monitoring.yml down

# View logs
docker-compose -f docker-compose-monitoring.yml logs -f
```

### Check Service Status
```bash
# Check all services
docker-compose -f docker-compose-monitoring.yml ps

# Check specific service
docker logs jarvis_grafana
docker logs jarvis_prometheus
docker logs jarvis_alertmanager
```

### Restart Services
```bash
# Restart all monitoring services
docker-compose -f docker-compose-monitoring.yml restart

# Restart specific service
docker-compose -f docker-compose-monitoring.yml restart grafana
```

## 🛠️ Troubleshooting

### Common Issues

#### Grafana Not Loading
1. Check if container is running: `docker ps | grep grafana`
2. Check logs: `docker logs jarvis_grafana`
3. Verify port 3000 is not in use: `netstat -tulpn | grep 3000`

#### No Metrics Showing
1. Verify JARVIS metrics server is running on port 9090
2. Check Prometheus targets: http://localhost:9091/targets
3. Ensure Prometheus can reach host.docker.internal:9090

#### Alerts Not Working
1. Check Alertmanager status: http://localhost:9093
2. Verify alert rules in Prometheus: http://localhost:9091/alerts
3. Check webhook configuration in `monitoring/alertmanager.yml`

### Performance Optimization

#### High Resource Usage
- Adjust scrape intervals in `monitoring/prometheus.yml`
- Reduce retention time for metrics
- Limit dashboard refresh rates

#### Storage Management
- Monitor Docker volume sizes: `docker system df`
- Clean old metrics: Adjust retention settings
- Backup important dashboards

## 📋 Maintenance Tasks

### Daily
- Check system health in Grafana dashboard
- Review error rates and investigate spikes
- Monitor resource usage trends

### Weekly
- Review alert configurations
- Check for system updates
- Analyze performance trends

### Monthly
- Clean up old metrics data
- Review and optimize dashboard queries
- Update monitoring configurations as needed

## 🎯 Best Practices

### Dashboard Usage
- Create custom dashboards for specific use cases
- Use time range selectors effectively
- Set up alerts for critical metrics
- Share dashboards with team members

### Query Optimization
- Use appropriate time ranges for queries
- Avoid overly complex queries in dashboards
- Use recording rules for frequently used queries
- Monitor query performance in Prometheus

### Alert Management
- Set meaningful alert thresholds
- Avoid alert fatigue with proper grouping
- Test alert notifications regularly
- Document alert response procedures

---

## 📞 Quick Reference

**Emergency Commands:**
```bash
# Stop all monitoring
docker-compose -f docker-compose-monitoring.yml down

# Restart monitoring stack
docker-compose -f docker-compose-monitoring.yml restart

# View all logs
docker-compose -f docker-compose-monitoring.yml logs
```

**Key URLs:**
- Dashboard: http://localhost:3000 (admin/jarvis123)
- Metrics: http://localhost:9091
- Alerts: http://localhost:9093
- Raw Data: http://localhost:9090/metrics

---
*For additional help, see troubleshooting/common_issues.md*
