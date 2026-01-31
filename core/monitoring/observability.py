"""
Monitoring and Observability - Simple monitoring system
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: float
    source: str
    resolved: bool = False

class SimpleMetrics:
    """Simple metrics collection"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
    
    def counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Record counter metric"""
        self.counters[name] = self.counters.get(name, 0) + value
        self.metrics.append(Metric(name, value, time.time(), labels))
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record gauge metric"""
        self.gauges[name] = value
        self.metrics.append(Metric(name, value, time.time(), labels))
    
    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """Get metrics"""
        if name:
            return [m for m in self.metrics if m.name == name]
        return self.metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "total_metrics": len(self.metrics),
            "counters": self.counters,
            "gauges": self.gauges,
            "last_updated": time.time()
        }

class SimpleAlerting:
    """Simple alerting system"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: Dict[str, Dict] = {}
    
    def add_rule(self, name: str, condition: str, level: AlertLevel, message: str):
        """Add alerting rule"""
        self.rules[name] = {
            "condition": condition,
            "level": level,
            "message": message
        }
    
    def trigger_alert(self, level: AlertLevel, message: str, source: str = "system"):
        """Trigger alert"""
        alert = Alert(level, message, time.time(), source)
        self.alerts.append(alert)
        
        # Simple console output for now
        print(f"🚨 ALERT [{level.value.upper()}] {message} (from: {source})")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return [a for a in self.alerts if not a.resolved]
    
    def resolve_alert(self, alert_index: int):
        """Resolve alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].resolved = True

class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.checks: Dict[str, bool] = {}
        self.last_check: float = 0
    
    def add_check(self, name: str, check_func):
        """Add health check"""
        self.checks[name] = check_func
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                if callable(check_func):
                    result = check_func()
                else:
                    result = True
                
                results[name] = {"status": "healthy" if result else "unhealthy", "checked_at": time.time()}
                if not result:
                    overall_healthy = False
            except Exception as e:
                results[name] = {"status": "error", "error": str(e), "checked_at": time.time()}
                overall_healthy = False
        
        self.last_check = time.time()
        
        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "checks": results,
            "last_check": self.last_check
        }

class MonitoringDashboard:
    """Simple monitoring dashboard data"""
    
    def __init__(self, metrics: SimpleMetrics, alerting: SimpleAlerting, health: HealthChecker):
        self.metrics = metrics
        self.alerting = alerting
        self.health = health
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        health_status = await self.health.run_health_checks()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": health_status,
            "metrics_summary": self.metrics.get_summary(),
            "active_alerts": len(self.alerting.get_active_alerts()),
            "recent_alerts": [asdict(a) for a in self.alerting.alerts[-5:]],  # Last 5 alerts
            "uptime": time.time() - (self.health.last_check or time.time()),
            "status": "operational"
        }

# Global monitoring instances
metrics = SimpleMetrics()
alerting = SimpleAlerting()
health_checker = HealthChecker()
dashboard = MonitoringDashboard(metrics, alerting, health_checker)

# Add default health checks
health_checker.add_check("memory_usage", lambda: True)  # Placeholder
health_checker.add_check("disk_space", lambda: True)    # Placeholder
health_checker.add_check("system_load", lambda: True)   # Placeholder

# Add default alerting rules
alerting.add_rule("high_error_rate", "error_rate > 0.1", AlertLevel.WARNING, "High error rate detected")
alerting.add_rule("system_down", "health_check_failed", AlertLevel.CRITICAL, "System health check failed")
