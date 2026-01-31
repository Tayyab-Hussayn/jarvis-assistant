#!/usr/bin/env python3
"""
JARVIS Metrics Collection System - Prometheus integration
"""

import time
import psutil
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
import threading

@dataclass
class MetricData:
    """Metric data structure"""
    name: str
    value: float
    labels: Dict[str, str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.timestamp is None:
            self.timestamp = time.time()

class JarvisMetrics:
    """JARVIS metrics collection and export"""
    
    def __init__(self, port: int = 9090):
        self.port = port
        self.logger = logging.getLogger("jarvis_metrics")
        
        # System metrics
        self.cpu_usage = Gauge('jarvis_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('jarvis_memory_usage_bytes', 'Memory usage in bytes')
        self.memory_percent = Gauge('jarvis_memory_usage_percent', 'Memory usage percentage')
        self.disk_usage = Gauge('jarvis_disk_usage_percent', 'Disk usage percentage')
        
        # JARVIS-specific metrics
        self.workflow_total = Counter('jarvis_workflows_total', 'Total workflows executed', ['status', 'engine'])
        self.workflow_duration = Histogram('jarvis_workflow_duration_seconds', 'Workflow execution time', ['workflow_type'])
        self.tool_executions = Counter('jarvis_tool_executions_total', 'Total tool executions', ['tool_name', 'status'])
        self.tool_duration = Histogram('jarvis_tool_duration_seconds', 'Tool execution time', ['tool_name'])
        
        # LLM metrics
        self.llm_requests = Counter('jarvis_llm_requests_total', 'Total LLM requests', ['provider', 'model'])
        self.llm_tokens = Counter('jarvis_llm_tokens_total', 'Total LLM tokens used', ['provider', 'type'])
        self.llm_duration = Histogram('jarvis_llm_duration_seconds', 'LLM request duration', ['provider'])
        
        # Error metrics
        self.errors_total = Counter('jarvis_errors_total', 'Total errors', ['component', 'error_type'])
        
        # Health metrics
        self.health_status = Gauge('jarvis_health_status', 'Health status (1=healthy, 0=unhealthy)', ['component'])
        self.uptime_seconds = Gauge('jarvis_uptime_seconds', 'Uptime in seconds')
        
        # Component info
        self.info = Info('jarvis_info', 'JARVIS system information')
        
        # Start time for uptime calculation
        self.start_time = time.time()
        
        # Metrics server
        self.server_started = False
    
    def start_metrics_server(self):
        """Start Prometheus metrics server"""
        if not self.server_started:
            try:
                start_http_server(self.port)
                self.server_started = True
                self.logger.info(f"✅ Metrics server started on port {self.port}")
                
                # Set system info
                import platform
                self.info.info({
                    'version': '1.0.0',
                    'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
                    'platform': platform.system(),
                    'start_time': str(datetime.fromtimestamp(self.start_time))
                })
                
            except Exception as e:
                self.logger.error(f"❌ Failed to start metrics server: {e}")
    
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)
            self.memory_percent.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_usage.set(disk_percent)
            
            # Uptime
            uptime = time.time() - self.start_time
            self.uptime_seconds.set(uptime)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def record_workflow_execution(self, workflow_type: str, duration: float, status: str, engine: str):
        """Record workflow execution metrics"""
        self.workflow_total.labels(status=status, engine=engine).inc()
        self.workflow_duration.labels(workflow_type=workflow_type).observe(duration)
    
    def record_tool_execution(self, tool_name: str, duration: float, status: str):
        """Record tool execution metrics"""
        self.tool_executions.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)
    
    def record_llm_request(self, provider: str, model: str, duration: float, tokens_used: int):
        """Record LLM request metrics"""
        self.llm_requests.labels(provider=provider, model=model).inc()
        self.llm_tokens.labels(provider=provider, type='total').inc(tokens_used)
        self.llm_duration.labels(provider=provider).observe(duration)
    
    def record_error(self, component: str, error_type: str):
        """Record error metrics"""
        self.errors_total.labels(component=component, error_type=error_type).inc()
    
    def set_health_status(self, component: str, healthy: bool):
        """Set component health status"""
        self.health_status.labels(component=component).set(1 if healthy else 0)
    
    async def start_background_collection(self):
        """Start background metrics collection"""
        self.start_metrics_server()
        
        while True:
            try:
                self.collect_system_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in background collection: {e}")
                await asyncio.sleep(60)  # Wait longer on error

class HealthChecker:
    """Health check system for JARVIS components"""
    
    def __init__(self, metrics: JarvisMetrics):
        self.metrics = metrics
        self.logger = logging.getLogger("health_checker")
        self.components = {}
    
    def register_component(self, name: str, check_func):
        """Register a component health check"""
        self.components[name] = check_func
        self.logger.info(f"Registered health check for: {name}")
    
    async def check_all_components(self) -> Dict[str, bool]:
        """Check health of all registered components"""
        results = {}
        
        for name, check_func in self.components.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    healthy = await check_func()
                else:
                    healthy = check_func()
                
                results[name] = healthy
                self.metrics.set_health_status(name, healthy)
                
                status = "✅ HEALTHY" if healthy else "❌ UNHEALTHY"
                self.logger.debug(f"{name}: {status}")
                
            except Exception as e:
                results[name] = False
                self.metrics.set_health_status(name, False)
                self.metrics.record_error("health_checker", "check_failed")
                self.logger.error(f"Health check failed for {name}: {e}")
        
        return results
    
    async def start_health_monitoring(self, interval: int = 60):
        """Start continuous health monitoring"""
        self.logger.info("🏥 Starting health monitoring...")
        
        while True:
            try:
                results = await self.check_all_components()
                
                # Log overall health
                healthy_count = sum(1 for h in results.values() if h)
                total_count = len(results)
                
                if healthy_count == total_count:
                    self.logger.info(f"🟢 All {total_count} components healthy")
                else:
                    unhealthy = [name for name, healthy in results.items() if not healthy]
                    self.logger.warning(f"🟡 {healthy_count}/{total_count} components healthy. Unhealthy: {unhealthy}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(interval * 2)  # Wait longer on error

# Global metrics instance
jarvis_metrics = JarvisMetrics()
health_checker = HealthChecker(jarvis_metrics)
