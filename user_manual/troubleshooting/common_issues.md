# JARVIS Troubleshooting Guide

## 🚨 Common Issues & Solutions

### System Startup Issues

#### JARVIS Won't Start
**Symptoms**: Application fails to initialize
**Causes & Solutions**:
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Configuration errors**: Run `python config_cli.py validate`
- **Port conflicts**: Check if ports 9090, 3000, 9091 are available
- **Permission issues**: Ensure proper file permissions

#### Docker Services Not Starting
**Symptoms**: Docker containers fail to start
**Solutions**:
```bash
# Check Docker daemon
sudo systemctl status docker

# Check container logs
docker-compose -f docker-compose-monitoring.yml logs

# Restart services
docker-compose -f docker-compose-monitoring.yml restart
```

### Monitoring Issues

#### Grafana Dashboard Empty
**Symptoms**: No data showing in Grafana
**Solutions**:
1. Check Prometheus targets: http://localhost:9091/targets
2. Verify JARVIS metrics server: http://localhost:9090/metrics
3. Check Prometheus configuration:
```bash
docker logs jarvis_prometheus
```

#### Metrics Not Collecting
**Symptoms**: No metrics in Prometheus
**Solutions**:
1. Verify metrics server is running:
```bash
netstat -tulpn | grep 9090
```
2. Check firewall settings
3. Restart metrics collection:
```python
from core.monitoring.metrics import jarvis_metrics
jarvis_metrics.start_metrics_server()
```

### Configuration Issues

#### Environment Variables Not Loading
**Symptoms**: "Environment variable 'X' not found" warnings
**Solutions**:
1. Check .env file exists: `ls -la .env`
2. Verify variable syntax: `cat .env`
3. Source environment: `source .env`
4. Use config CLI: `python config_cli.py show`

#### Wrong Environment Loading
**Symptoms**: Unexpected configuration values
**Solutions**:
1. Check environment variable: `echo $JARVIS_ENV`
2. Set correct environment: `export JARVIS_ENV=development`
3. Validate configuration: `python config_cli.py validate`

### Workflow Issues

#### Temporal Workflows Hanging
**Symptoms**: Workflows start but never complete
**Solutions**:
1. Check Temporal server status:
```bash
docker-compose -f docker-compose-temporal.yml ps
```
2. Verify worker is running
3. Check Temporal UI: http://localhost:8080
4. Restart Temporal services:
```bash
docker-compose -f docker-compose-temporal.yml restart
```

#### Simple Workflows Failing
**Symptoms**: Workflows fail with errors
**Solutions**:
1. Check tool registry: Verify tools are properly registered
2. Check execution engine: Ensure execution engine is initialized
3. Review error logs in monitoring dashboard

### Tool Execution Issues

#### Tool Not Found
**Symptoms**: "Tool 'X' not found" errors
**Solutions**:
1. Check tool registration:
```python
from modules.tools.base_tool import tool_registry
print(tool_registry.list_tools())
```
2. Verify tool imports
3. Check tool initialization

#### Permission Denied
**Symptoms**: Tool execution fails with permission errors
**Solutions**:
1. Check file permissions
2. Verify sandbox settings in configuration
3. Review allowed commands list
4. Check Docker permissions (if using Docker executor)

### LLM Integration Issues

#### API Key Not Working
**Symptoms**: LLM requests fail with authentication errors
**Solutions**:
1. Verify API key: `python config_cli.py show`
2. Check key format and validity
3. Test with different provider
4. Review rate limits

#### Slow LLM Responses
**Symptoms**: Long response times from LLM
**Solutions**:
1. Check network connectivity
2. Monitor LLM metrics in Grafana
3. Adjust timeout settings
4. Consider switching providers

### Database Issues

#### Database Connection Failed
**Symptoms**: Cannot connect to database
**Solutions**:
1. Check database URL in configuration
2. Verify database server is running
3. Test connection manually
4. Check network connectivity

#### Database Locked
**Symptoms**: SQLite database locked errors
**Solutions**:
1. Close other connections to database
2. Restart JARVIS application
3. Check for zombie processes
4. Consider switching to PostgreSQL for production

## 🔧 Diagnostic Commands

### System Health Check
```bash
# Check all services
docker-compose -f docker-compose-monitoring.yml ps
docker-compose -f docker-compose-temporal.yml ps

# Check JARVIS configuration
python config_cli.py test

# Check metrics endpoint
curl http://localhost:9090/metrics
```

### Log Analysis
```bash
# View monitoring logs
docker-compose -f docker-compose-monitoring.yml logs -f

# View Temporal logs
docker-compose -f docker-compose-temporal.yml logs -f

# Check system logs
journalctl -u docker.service -f
```

### Network Diagnostics
```bash
# Check port availability
netstat -tulpn | grep -E "(3000|9090|9091|7233|8080)"

# Test connectivity
curl -I http://localhost:3000
curl -I http://localhost:9091
curl -I http://localhost:8080
```

## 🚑 Emergency Procedures

### Complete System Reset
```bash
# Stop all services
docker-compose -f docker-compose-monitoring.yml down
docker-compose -f docker-compose-temporal.yml down

# Clean Docker resources
docker system prune -f

# Restart services
docker-compose -f docker-compose-temporal.yml up -d
docker-compose -f docker-compose-monitoring.yml up -d

# Restart JARVIS metrics
python -c "from core.monitoring.metrics import jarvis_metrics; jarvis_metrics.start_metrics_server()"
```

### Data Recovery
```bash
# Backup current data
docker run --rm -v jarvis_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus_backup.tar.gz /data
docker run --rm -v jarvis_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana_backup.tar.gz /data

# Restore from backup
docker run --rm -v jarvis_prometheus_data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus_backup.tar.gz -C /
```

## 📊 Performance Troubleshooting

### High CPU Usage
1. Check system metrics in Grafana
2. Identify resource-intensive processes
3. Adjust monitoring intervals
4. Optimize workflow execution

### High Memory Usage
1. Monitor memory metrics
2. Check for memory leaks
3. Adjust Docker container limits
4. Restart services if needed

### Slow Performance
1. Check network latency
2. Monitor database performance
3. Review LLM response times
4. Optimize configuration settings

## 🔍 Debug Mode

### Enable Debug Logging
```bash
# Set debug environment
export JARVIS_ENV=development

# Or edit configuration
# monitoring:
#   log_level: "DEBUG"
```

### Verbose Monitoring
```python
# Enable detailed metrics collection
from core.monitoring.metrics import jarvis_metrics
import logging

logging.getLogger("jarvis_metrics").setLevel(logging.DEBUG)
```

## 📞 Getting Help

### Information to Collect
1. **System Information**:
   - Operating system and version
   - Python version
   - Docker version
   - JARVIS configuration

2. **Error Details**:
   - Complete error messages
   - Stack traces
   - Log files
   - Steps to reproduce

3. **Environment**:
   - Environment variables
   - Configuration files
   - Service status

### Useful Commands for Support
```bash
# System information
uname -a
python --version
docker --version

# JARVIS status
python config_cli.py show
docker-compose -f docker-compose-monitoring.yml ps

# Recent logs
docker-compose -f docker-compose-monitoring.yml logs --tail=50
```

---
*For specific component guides, see the respective sections in the user manual*
