"""
JARVIS AI AGENT - DEVELOPMENT RULES & OPERATING PRINCIPLES
=========================================================

This file contains the core operating principles, development rules, and 
architectural guidelines that ALL agents working on this project must follow.
These rules ensure consistency, quality, and successful delivery.

CRITICAL: Every agent must read and follow these rules exactly.
"""

# ============================================================================
# CORE DEVELOPMENT PRINCIPLES
# ============================================================================

DEVELOPMENT_PHILOSOPHY = {
    "build_incrementally": "Build in layers, validate each before proceeding",
    "safety_first": "Every component must have safety guards and error handling", 
    "production_ready": "Build for 24/7 operation, not demos",
    "minimal_viable": "Write only the code needed to solve the requirement",
    "test_driven": "Every component needs validation criteria and tests",
    "observable": "Log everything, measure everything, monitor everything"
}

# ============================================================================
# ARCHITECTURAL RULES
# ============================================================================

ARCHITECTURE_RULES = {
    "dual_engine": "Separate Reasoning Engine (strategic) from Execution Engine (tactical)",
    "orchestration_layer": "Use Temporal.io for workflow management and state persistence",
    "event_driven": "Engines communicate via Redis pub/sub, never direct coupling",
    "sandboxing": "All code execution must be containerized with resource limits",
    "memory_hybrid": "Use Vector DB + PostgreSQL + Redis for different memory needs",
    "tool_registry": "Tools are registered dynamically, never hardcoded",
    "skill_framework": "Skills combine LLM knowledge with deterministic code"
}

# ============================================================================
# SAFETY & SECURITY RULES
# ============================================================================

SAFETY_RULES = {
    "command_blacklist": [
        "rm -rf /",
        ":(){ :|:& };:",  # Fork bomb
        "dd if=/dev/random of=/dev/sda",
        "chmod -R 777 /",
        "mkfs.*",
        "fdisk",
        "parted"
    ],
    
    "whitelist_directories": [
        "/home/krawin/exp.code/jarvis",
        "/tmp/jarvis_workspace",
        "/var/tmp/jarvis"
    ],
    
    "resource_limits": {
        "max_execution_time": 300,  # 5 minutes
        "max_memory_mb": 1024,
        "max_cpu_percent": 50,
        "max_disk_mb": 100
    },
    
    "approval_required": [
        "file_deletion",
        "system_modification", 
        "network_access",
        "package_installation",
        "service_management"
    ]
}

# ============================================================================
# CODE QUALITY STANDARDS
# ============================================================================

CODE_STANDARDS = {
    "python_style": "Follow PEP 8, use type hints, docstrings for all functions",
    "error_handling": "Never silent fail, always log errors, implement retry logic",
    "logging_format": "Structured JSON logging with correlation IDs",
    "testing_coverage": "Minimum 80% test coverage for all components",
    "documentation": "Every module needs README.md with usage examples",
    "dependency_management": "Pin all versions, use virtual environments"
}

# ============================================================================
# LAYER PROGRESSION RULES
# ============================================================================

LAYER_RULES = {
    "sequential_only": "Must complete current layer before starting next",
    "validation_required": "Each layer must pass validation criteria",
    "no_skipping": "Cannot skip tasks even if they seem optional",
    "dependency_respect": "Never start task until all dependencies completed",
    "rollback_on_failure": "If layer validation fails, fix before proceeding"
}

# ============================================================================
# TOOL DEVELOPMENT STANDARDS
# ============================================================================

TOOL_STANDARDS = {
    "base_class": "All tools must inherit from BaseTool",
    "validation": "Input validation using Pydantic schemas",
    "error_recovery": "Implement retry logic with exponential backoff",
    "result_structure": "Return structured results with success/failure status",
    "safety_checks": "Validate all inputs, sanitize outputs",
    "logging": "Log all tool executions with input/output/duration"
}

# Example Tool Template:
TOOL_TEMPLATE = '''
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict
import logging

class ToolResult(BaseModel):
    success: bool
    output: Any
    error_message: str = ""
    execution_time: float
    confidence: float = 1.0

class BaseTool(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        return True
    
    def handle_error(self, error: Exception) -> ToolResult:
        """Handle execution errors"""
        self.logger.error(f"Tool {self.name} failed: {error}")
        return ToolResult(
            success=False,
            output=None,
            error_message=str(error),
            execution_time=0.0
        )
'''

# ============================================================================
# SKILL DEVELOPMENT STANDARDS  
# ============================================================================

SKILL_STANDARDS = {
    "hybrid_approach": "Combine skill.md (LLM context) with .py (deterministic logic)",
    "skill_registry": "Skills registered in skills.yaml configuration",
    "tool_invocation": "Skills are invoked through tools, not directly by LLM",
    "context_injection": "skill.md provides context to LLM for decision making",
    "deterministic_core": ".py files handle critical logic that cannot fail"
}

# Example Skill Structure:
SKILL_STRUCTURE = '''
skills/
├── skill_name/
│   ├── skill.md              # LLM-readable description and examples
│   ├── skill_implementation.py  # Deterministic logic
│   ├── templates/            # Prompt templates
│   └── tests/               # Unit tests
'''

# ============================================================================
# MEMORY SYSTEM RULES
# ============================================================================

MEMORY_RULES = {
    "vector_db": "Use Qdrant for semantic search of experiences and knowledge",
    "relational_db": "Use PostgreSQL for structured data, logs, relationships", 
    "cache": "Use Redis for short-term memory and session state",
    "consolidation": "Implement background job to consolidate and prune memories",
    "semantic_search": "All memories must be searchable by semantic similarity",
    "privacy": "Never store sensitive data in plain text"
}

# ============================================================================
# WORKFLOW ENGINE RULES
# ============================================================================

WORKFLOW_RULES = {
    "temporal_workflows": "Use Temporal.io for all long-running workflows",
    "checkpoint_system": "Workflows must be resumable after system restart",
    "human_in_loop": "Implement approval gates for critical operations",
    "event_triggers": "Support email, file, schedule, and manual triggers",
    "parallel_execution": "Execute independent tasks in parallel when possible",
    "failure_recovery": "Implement retry and escalation strategies"
}

# ============================================================================
# TESTING & VALIDATION RULES
# ============================================================================

TESTING_RULES = {
    "unit_tests": "Every function/class needs unit tests",
    "integration_tests": "Test engine interactions and workflows",
    "end_to_end_tests": "Test complete user scenarios",
    "performance_tests": "Measure response times and resource usage",
    "safety_tests": "Test all safety mechanisms and edge cases",
    "continuous_testing": "Run tests on every commit"
}

# ============================================================================
# MONITORING & OBSERVABILITY RULES
# ============================================================================

MONITORING_RULES = {
    "structured_logging": "Use JSON format with correlation IDs",
    "metrics_collection": "Prometheus metrics for all components",
    "distributed_tracing": "OpenTelemetry for request flow tracking",
    "alerting": "Alert on failures, performance degradation, resource limits",
    "dashboards": "Grafana dashboards for real-time monitoring",
    "health_checks": "Every service needs health check endpoint"
}

# ============================================================================
# COMMUNICATION PROTOCOLS
# ============================================================================

COMMUNICATION_RULES = {
    "event_bus": "Use Redis Streams for inter-engine communication",
    "message_format": "Structured JSON messages with schema validation",
    "async_processing": "All inter-engine communication is asynchronous",
    "correlation_ids": "Track requests across all components",
    "timeout_handling": "All communications have timeout and retry logic",
    "circuit_breaker": "Implement circuit breaker for external services"
}

# ============================================================================
# PERFORMANCE RULES
# ============================================================================

PERFORMANCE_RULES = {
    "response_time": "Target <2 seconds for simple tasks, <30 seconds for complex",
    "caching_strategy": "Cache LLM responses, tool results, and computed data",
    "resource_monitoring": "Monitor CPU, memory, disk usage continuously",
    "optimization_targets": "Optimize hot paths identified through profiling",
    "scalability": "Design for horizontal scaling of stateless components",
    "cost_optimization": "Use local LLM for simple tasks, Claude for complex"
}

# ============================================================================
# DEPLOYMENT RULES
# ============================================================================

DEPLOYMENT_RULES = {
    "containerization": "All components run in Docker containers",
    "environment_separation": "Separate dev, staging, production environments",
    "configuration_management": "Use environment variables and config files",
    "secret_management": "Never commit secrets, use secure secret storage",
    "backup_strategy": "Regular backups of databases and critical data",
    "rollback_capability": "Ability to rollback to previous version quickly"
}

# ============================================================================
# AGENT COLLABORATION RULES
# ============================================================================

COLLABORATION_RULES = {
    "progress_tracking": "Update PROGRESS_TRACKER.py after completing tasks",
    "documentation": "Document all decisions and architectural changes",
    "code_review": "All code changes need review and validation",
    "knowledge_sharing": "Share learnings and solutions with team",
    "consistency": "Follow established patterns and conventions",
    "communication": "Clear communication about blockers and dependencies"
}

# ============================================================================
# EMERGENCY PROCEDURES
# ============================================================================

EMERGENCY_PROCEDURES = {
    "system_failure": "Implement graceful degradation and recovery procedures",
    "data_corruption": "Backup and restore procedures for all data stores",
    "security_breach": "Incident response plan for security issues",
    "performance_degradation": "Procedures for identifying and fixing bottlenecks",
    "dependency_failure": "Fallback strategies for external service failures",
    "human_escalation": "Clear escalation path when automated recovery fails"
}

# ============================================================================
# SUCCESS METRICS
# ============================================================================

SUCCESS_METRICS = {
    "reliability": "99.9% uptime for 24/7 operation",
    "performance": "Sub-second response for 90% of requests",
    "accuracy": "95%+ task completion success rate",
    "user_satisfaction": "Feels natural and helpful like Jarvis",
    "learning_capability": "Demonstrable improvement over time",
    "safety": "Zero security incidents or data breaches"
}

# ============================================================================
# FINAL REMINDERS
# ============================================================================

CRITICAL_REMINDERS = [
    "🚨 NEVER skip validation criteria - they prevent technical debt",
    "🔒 ALWAYS implement safety checks - we're building production software",
    "📊 MEASURE everything - you can't improve what you don't measure",
    "🧪 TEST thoroughly - bugs in production are expensive to fix",
    "📝 DOCUMENT decisions - future developers will thank you",
    "🔄 FOLLOW the layer progression - shortcuts lead to architectural debt",
    "🎯 FOCUS on the current task - don't get distracted by future features",
    "🤝 COMMUNICATE blockers early - don't struggle in silence"
]

if __name__ == "__main__":
    print("JARVIS AI AGENT - DEVELOPMENT RULES")
    print("=" * 50)
    print("These rules ensure we build a production-grade AI agent.")
    print("Every agent working on this project must follow these exactly.")
    print("\nCritical Reminders:")
    for reminder in CRITICAL_REMINDERS:
        print(f"  {reminder}")
