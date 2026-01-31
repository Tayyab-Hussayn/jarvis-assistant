"""
Recovery System - Handle failures and implement retry strategies
"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from modules.tools.base_tool import ToolResult, ToolStatus

class RecoveryStrategy(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    SKIP = "skip"
    ABORT = "abort"

class FailureCategory(Enum):
    TRANSIENT = "transient"  # Network timeouts, temporary unavailability
    CONFIGURATION = "configuration"  # Wrong parameters, missing config
    LOGIC = "logic"  # Code errors, invalid operations
    RESOURCE = "resource"  # Out of memory, disk space, etc.
    PERMISSION = "permission"  # Access denied, authentication
    FATAL = "fatal"  # Unrecoverable errors

@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True
    backoff_strategy: str = "exponential"  # "exponential", "linear", "fixed"

@dataclass
class RecoveryAction:
    strategy: RecoveryStrategy
    config: Dict[str, Any] = field(default_factory=dict)
    fallback_tool: Optional[str] = None
    escalation_handler: Optional[Callable] = None
    condition: Optional[str] = None

@dataclass
class FailureRecord:
    tool_name: str
    error_message: str
    category: FailureCategory
    timestamp: float
    attempt_number: int
    recovery_action: RecoveryAction
    context: Dict[str, Any] = field(default_factory=dict)

class RecoverySystem:
    """Handle failures and implement recovery strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger("recovery_system")
        
        # Failure history for pattern analysis
        self.failure_history: List[FailureRecord] = []
        
        # Default recovery strategies by failure category
        self.default_strategies = {
            FailureCategory.TRANSIENT: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                config={"max_attempts": 3, "base_delay": 2.0}
            ),
            FailureCategory.CONFIGURATION: RecoveryAction(
                strategy=RecoveryStrategy.ESCALATE,
                config={"require_human": True}
            ),
            FailureCategory.LOGIC: RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                config={"try_alternative": True}
            ),
            FailureCategory.RESOURCE: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                config={"max_attempts": 2, "base_delay": 5.0}
            ),
            FailureCategory.PERMISSION: RecoveryAction(
                strategy=RecoveryStrategy.ESCALATE,
                config={"require_human": True}
            ),
            FailureCategory.FATAL: RecoveryAction(
                strategy=RecoveryStrategy.ABORT,
                config={}
            )
        }
        
        # Tool fallback mappings
        self.tool_fallbacks = {
            "web_search": ["file_manager"],  # If web search fails, try local files
            "terminal_executor": ["file_manager"],  # If terminal fails, try file operations
            "code_executor": ["terminal_executor"],  # If code execution fails, try terminal
        }
        
        # Error pattern to category mapping
        self.error_patterns = {
            FailureCategory.TRANSIENT: [
                "timeout", "connection", "network", "temporary", "unavailable",
                "busy", "rate limit", "throttle"
            ],
            FailureCategory.CONFIGURATION: [
                "config", "parameter", "argument", "missing", "invalid",
                "not found", "does not exist"
            ],
            FailureCategory.LOGIC: [
                "syntax", "parse", "format", "invalid", "unexpected",
                "assertion", "logic", "algorithm"
            ],
            FailureCategory.RESOURCE: [
                "memory", "disk", "space", "limit", "quota", "resource",
                "capacity", "full"
            ],
            FailureCategory.PERMISSION: [
                "permission", "access", "denied", "forbidden", "unauthorized",
                "authentication", "credential"
            ],
            FailureCategory.FATAL: [
                "fatal", "critical", "system", "crash", "corruption",
                "unrecoverable"
            ]
        }
    
    def categorize_failure(self, error_message: str, tool_name: str = "") -> FailureCategory:
        """Categorize failure based on error message and context"""
        
        error_lower = error_message.lower()
        
        # Check patterns for each category
        for category, patterns in self.error_patterns.items():
            if any(pattern in error_lower for pattern in patterns):
                return category
        
        # Default to logic error if no pattern matches
        return FailureCategory.LOGIC
    
    async def handle_failure(self, tool_name: str, result: ToolResult, 
                           attempt_number: int = 1, context: Dict[str, Any] = None) -> Tuple[RecoveryStrategy, Dict[str, Any]]:
        """Handle a tool failure and determine recovery strategy"""
        
        if context is None:
            context = {}
        
        # Categorize the failure
        category = self.categorize_failure(result.error_message, tool_name)
        
        # Get recovery action
        recovery_action = self._get_recovery_action(tool_name, category, attempt_number, context)
        
        # Record failure
        failure_record = FailureRecord(
            tool_name=tool_name,
            error_message=result.error_message,
            category=category,
            timestamp=time.time(),
            attempt_number=attempt_number,
            recovery_action=recovery_action,
            context=context
        )
        
        self.failure_history.append(failure_record)
        
        self.logger.warning(f"Failure in {tool_name} (attempt {attempt_number}): {category.value} - {result.error_message}")
        self.logger.info(f"Recovery strategy: {recovery_action.strategy.value}")
        
        return recovery_action.strategy, recovery_action.config
    
    def _get_recovery_action(self, tool_name: str, category: FailureCategory, 
                           attempt_number: int, context: Dict[str, Any]) -> RecoveryAction:
        """Get appropriate recovery action for the failure"""
        
        # Check for tool-specific recovery rules
        tool_specific_action = self._get_tool_specific_action(tool_name, category, attempt_number)
        if tool_specific_action:
            return tool_specific_action
        
        # Use default strategy for category
        default_action = self.default_strategies.get(category)
        if not default_action:
            return RecoveryAction(strategy=RecoveryStrategy.ESCALATE)
        
        # Modify action based on attempt number
        if attempt_number >= 3 and default_action.strategy == RecoveryStrategy.RETRY:
            # After 3 attempts, escalate or try fallback
            if tool_name in self.tool_fallbacks:
                return RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK,
                    fallback_tool=self.tool_fallbacks[tool_name][0]
                )
            else:
                return RecoveryAction(strategy=RecoveryStrategy.ESCALATE)
        
        return default_action
    
    def _get_tool_specific_action(self, tool_name: str, category: FailureCategory, 
                                attempt_number: int) -> Optional[RecoveryAction]:
        """Get tool-specific recovery action"""
        
        # Tool-specific recovery rules
        if tool_name == "web_search" and category == FailureCategory.TRANSIENT:
            return RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                config={"max_attempts": 2, "base_delay": 5.0}
            )
        
        elif tool_name == "terminal_executor" and category == FailureCategory.PERMISSION:
            return RecoveryAction(
                strategy=RecoveryStrategy.ESCALATE,
                config={"suggest_sudo": True}
            )
        
        elif tool_name == "code_executor" and category == FailureCategory.RESOURCE:
            return RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                config={"reduce_memory": True, "max_attempts": 2}
            )
        
        return None
    
    async def execute_with_recovery(self, tool_executor: Callable, tool_name: str, 
                                  max_recovery_attempts: int = 3, **kwargs) -> ToolResult:
        """Execute a tool with automatic recovery on failure"""
        
        attempt = 1
        last_result = None
        
        while attempt <= max_recovery_attempts:
            try:
                # Execute the tool
                result = await tool_executor(**kwargs)
                
                if result.success:
                    if attempt > 1:
                        self.logger.info(f"Tool {tool_name} succeeded on attempt {attempt}")
                    return result
                
                # Handle failure
                strategy, config = await self.handle_failure(tool_name, result, attempt, kwargs)
                last_result = result
                
                if strategy == RecoveryStrategy.ABORT:
                    self.logger.error(f"Aborting execution of {tool_name}")
                    break
                
                elif strategy == RecoveryStrategy.SKIP:
                    self.logger.info(f"Skipping failed tool {tool_name}")
                    # Return a success result with empty output
                    return ToolResult(
                        success=True,
                        output="",
                        metadata={"skipped": True, "original_error": result.error_message}
                    )
                
                elif strategy == RecoveryStrategy.ESCALATE:
                    self.logger.warning(f"Escalating failure in {tool_name}")
                    await self._escalate_failure(tool_name, result, config)
                    break
                
                elif strategy == RecoveryStrategy.FALLBACK:
                    # Remove config from kwargs to avoid duplicate parameter
                    fallback_kwargs = {k: v for k, v in kwargs.items() if k != 'config'}
                    fallback_result = await self._try_fallback(tool_name, config, **fallback_kwargs)
                    if fallback_result and fallback_result.success:
                        return fallback_result
                
                elif strategy == RecoveryStrategy.RETRY:
                    retry_config = RetryConfig(**config)
                    delay = self._calculate_delay(attempt, retry_config)
                    
                    self.logger.info(f"Retrying {tool_name} in {delay:.1f} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                attempt += 1
                
            except Exception as e:
                self.logger.error(f"Unexpected error in {tool_name}: {e}")
                last_result = ToolResult(
                    success=False,
                    output=None,
                    error_message=str(e),
                    status=ToolStatus.FAILURE
                )
                break
        
        # All recovery attempts failed
        self.logger.error(f"All recovery attempts failed for {tool_name}")
        return last_result or ToolResult(
            success=False,
            output=None,
            error_message="All recovery attempts failed",
            status=ToolStatus.FAILURE
        )
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for retry attempt"""
        
        if config.backoff_strategy == "exponential":
            delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        elif config.backoff_strategy == "linear":
            delay = config.base_delay * attempt
        else:  # fixed
            delay = config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.1, delay)  # Minimum 0.1 second delay
    
    async def _try_fallback(self, original_tool: str, config: Dict[str, Any], **kwargs) -> Optional[ToolResult]:
        """Try fallback tool"""
        
        fallback_tool = config.get("fallback_tool")
        if not fallback_tool:
            fallback_tools = self.tool_fallbacks.get(original_tool, [])
            if fallback_tools:
                fallback_tool = fallback_tools[0]
        
        if not fallback_tool:
            self.logger.warning(f"No fallback tool available for {original_tool}")
            return None
        
        self.logger.info(f"Trying fallback tool {fallback_tool} for {original_tool}")
        
        try:
            # Import and execute fallback tool
            from modules.tools.base_tool import tool_registry
            result = await tool_registry.execute_tool(fallback_tool, **kwargs)
            
            if result.success:
                self.logger.info(f"Fallback tool {fallback_tool} succeeded")
                result.metadata = result.metadata or {}
                result.metadata["fallback_for"] = original_tool
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fallback tool {fallback_tool} also failed: {e}")
            return None
    
    async def _escalate_failure(self, tool_name: str, result: ToolResult, config: Dict[str, Any]):
        """Escalate failure to human or higher-level system"""
        
        escalation_message = f"""
Tool Failure Escalation:
- Tool: {tool_name}
- Error: {result.error_message}
- Requires human intervention: {config.get('require_human', False)}
- Suggested action: {config.get('suggestion', 'Review and fix the issue')}
"""
        
        self.logger.critical(escalation_message)
        
        # In production, this would:
        # 1. Send notification to human operator
        # 2. Create support ticket
        # 3. Pause workflow until resolved
        
        # For now, just log the escalation
        if config.get("require_human"):
            self.logger.info("Human intervention required - workflow paused")
    
    def get_failure_patterns(self, tool_name: Optional[str] = None, 
                           time_window: int = 3600) -> Dict[str, Any]:
        """Analyze failure patterns for insights"""
        
        current_time = time.time()
        recent_failures = [
            f for f in self.failure_history 
            if current_time - f.timestamp <= time_window
        ]
        
        if tool_name:
            recent_failures = [f for f in recent_failures if f.tool_name == tool_name]
        
        if not recent_failures:
            return {"total_failures": 0}
        
        # Analyze patterns
        category_counts = {}
        tool_counts = {}
        error_patterns = {}
        
        for failure in recent_failures:
            # Count by category
            category_counts[failure.category.value] = category_counts.get(failure.category.value, 0) + 1
            
            # Count by tool
            tool_counts[failure.tool_name] = tool_counts.get(failure.tool_name, 0) + 1
            
            # Extract error patterns
            error_words = failure.error_message.lower().split()
            for word in error_words:
                if len(word) > 3:  # Skip short words
                    error_patterns[word] = error_patterns.get(word, 0) + 1
        
        # Find most common error patterns
        common_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_failures": len(recent_failures),
            "category_breakdown": category_counts,
            "tool_breakdown": tool_counts,
            "common_error_patterns": common_errors,
            "failure_rate": len(recent_failures) / max(1, time_window / 60),  # failures per minute
            "time_window_hours": time_window / 3600
        }
    
    def suggest_improvements(self, tool_name: Optional[str] = None) -> List[str]:
        """Suggest improvements based on failure patterns"""
        
        patterns = self.get_failure_patterns(tool_name)
        suggestions = []
        
        if patterns["total_failures"] == 0:
            return ["No recent failures - system is performing well"]
        
        # High failure rate
        if patterns["failure_rate"] > 1:  # More than 1 failure per minute
            suggestions.append("High failure rate detected - consider system health check")
        
        # Category-specific suggestions
        category_breakdown = patterns.get("category_breakdown", {})
        
        if category_breakdown.get("transient", 0) > 5:
            suggestions.append("Many transient failures - check network connectivity and external services")
        
        if category_breakdown.get("configuration", 0) > 2:
            suggestions.append("Configuration errors detected - review tool parameters and settings")
        
        if category_breakdown.get("resource", 0) > 2:
            suggestions.append("Resource issues detected - monitor system resources and consider scaling")
        
        # Tool-specific suggestions
        tool_breakdown = patterns.get("tool_breakdown", {})
        problematic_tools = [tool for tool, count in tool_breakdown.items() if count > 3]
        
        if problematic_tools:
            suggestions.append(f"Tools with high failure rates: {', '.join(problematic_tools)} - consider maintenance")
        
        return suggestions or ["No specific improvement suggestions at this time"]

# Global recovery system instance
recovery_system = RecoverySystem()
