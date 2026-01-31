"""
Tool Orchestrator - Route tasks to appropriate tools and chain operations
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus, tool_registry

class ChainStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

@dataclass
class ToolChainStep:
    step_id: str
    tool_name: str
    parameters: Dict[str, Any]
    depends_on: List[str] = None  # Step IDs this depends on
    condition: Optional[str] = None  # Condition for execution
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

@dataclass
class ToolChain:
    chain_id: str
    name: str
    description: str
    steps: List[ToolChainStep]
    strategy: ChainStrategy
    timeout: int = 300  # 5 minutes default

@dataclass
class ChainExecutionResult:
    chain_id: str
    success: bool
    step_results: Dict[str, ToolResult]
    execution_time: float
    error_message: str = ""
    completed_steps: List[str] = None
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []

class ToolOrchestrator:
    """Orchestrate tool execution with chaining and routing"""
    
    def __init__(self):
        self.logger = logging.getLogger("tool_orchestrator")
        self.active_chains: Dict[str, ChainExecutionResult] = {}
        
        # Tool routing rules
        self.routing_rules = {
            "file_operations": ["file_manager"],
            "system_commands": ["terminal_executor"],
            "calculations": ["calculator"],
            "web_research": ["web_search"],
            "user_interaction": ["human_input"],
            "text_processing": ["file_manager"],
            "data_analysis": ["calculator", "file_manager"]
        }
        
        # Tool compatibility matrix
        self.tool_compatibility = {
            "file_manager": ["terminal_executor", "calculator"],
            "terminal_executor": ["file_manager"],
            "web_search": ["file_manager"],
            "calculator": ["file_manager"],
            "human_input": ["file_manager", "terminal_executor"]
        }
    
    def route_task_to_tools(self, task_description: str) -> List[str]:
        """Route a task to appropriate tools based on description"""
        
        task_lower = task_description.lower()
        suggested_tools = []
        
        # Keyword-based routing
        routing_keywords = {
            "file_manager": ["file", "read", "write", "create", "save", "document", "text"],
            "terminal_executor": ["command", "execute", "run", "install", "system", "shell"],
            "web_search": ["search", "research", "find", "lookup", "web", "internet"],
            "calculator": ["calculate", "compute", "math", "number", "sum", "count"],
            "human_input": ["ask", "confirm", "input", "user", "approval", "question"]
        }
        
        for tool_name, keywords in routing_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                if tool_name not in suggested_tools:
                    suggested_tools.append(tool_name)
        
        # If no specific tools found, default to file_manager for basic tasks
        if not suggested_tools:
            suggested_tools = ["file_manager"]
        
        self.logger.info(f"Routed task '{task_description}' to tools: {suggested_tools}")
        return suggested_tools
    
    def create_tool_chain(self, task_description: str, steps: List[Dict]) -> ToolChain:
        """Create a tool chain from task description and steps"""
        
        chain_id = f"chain_{len(self.active_chains)+1:03d}"
        
        chain_steps = []
        for i, step_data in enumerate(steps):
            step = ToolChainStep(
                step_id=f"step_{i+1:02d}",
                tool_name=step_data.get("tool", "file_manager"),
                parameters=step_data.get("parameters", {}),
                depends_on=step_data.get("depends_on", []),
                condition=step_data.get("condition")
            )
            chain_steps.append(step)
        
        chain = ToolChain(
            chain_id=chain_id,
            name=f"Chain for: {task_description}",
            description=task_description,
            steps=chain_steps,
            strategy=ChainStrategy.SEQUENTIAL,  # Default to sequential
            timeout=600  # 10 minutes for chains
        )
        
        self.logger.info(f"Created tool chain {chain_id} with {len(chain_steps)} steps")
        return chain
    
    async def execute_single_tool(self, tool_name: str, **parameters) -> ToolResult:
        """Execute a single tool with parameters"""
        
        self.logger.info(f"Executing tool: {tool_name}")
        
        # Get tool from registry
        result = await tool_registry.execute_tool(tool_name, **parameters)
        
        if result.success:
            self.logger.info(f"Tool {tool_name} executed successfully")
        else:
            self.logger.error(f"Tool {tool_name} failed: {result.error_message}")
        
        return result
    
    async def execute_tool_chain(self, chain: ToolChain) -> ChainExecutionResult:
        """Execute a complete tool chain"""
        
        start_time = asyncio.get_event_loop().time()
        self.logger.info(f"Executing tool chain: {chain.chain_id}")
        
        result = ChainExecutionResult(
            chain_id=chain.chain_id,
            success=True,
            step_results={},
            execution_time=0.0
        )
        
        self.active_chains[chain.chain_id] = result
        
        try:
            if chain.strategy == ChainStrategy.SEQUENTIAL:
                await self._execute_sequential_chain(chain, result)
            elif chain.strategy == ChainStrategy.PARALLEL:
                await self._execute_parallel_chain(chain, result)
            elif chain.strategy == ChainStrategy.CONDITIONAL:
                await self._execute_conditional_chain(chain, result)
            
            result.execution_time = asyncio.get_event_loop().time() - start_time
            
            # Check overall success
            failed_steps = [step_id for step_id, step_result in result.step_results.items() 
                          if not step_result.success]
            
            if failed_steps:
                result.success = False
                result.error_message = f"Failed steps: {', '.join(failed_steps)}"
            
            self.logger.info(f"Chain {chain.chain_id} completed: success={result.success}")
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Chain {chain.chain_id} failed: {e}")
        
        return result
    
    async def _execute_sequential_chain(self, chain: ToolChain, result: ChainExecutionResult):
        """Execute chain steps sequentially"""
        
        for step in chain.steps:
            # Check dependencies
            if not self._check_dependencies(step, result):
                result.success = False
                result.error_message = f"Dependencies not met for step {step.step_id}"
                break
            
            # Check condition
            if step.condition and not self._evaluate_condition(step.condition, result):
                self.logger.info(f"Skipping step {step.step_id} due to condition: {step.condition}")
                continue
            
            # Execute step
            step_result = await self.execute_single_tool(step.tool_name, **step.parameters)
            result.step_results[step.step_id] = step_result
            
            if step_result.success:
                result.completed_steps.append(step.step_id)
            else:
                # Stop on failure in sequential execution
                result.success = False
                result.error_message = f"Step {step.step_id} failed: {step_result.error_message}"
                break
    
    async def _execute_parallel_chain(self, chain: ToolChain, result: ChainExecutionResult):
        """Execute chain steps in parallel where possible"""
        
        # Group steps by dependency level
        dependency_levels = self._group_by_dependencies(chain.steps)
        
        for level_steps in dependency_levels:
            # Execute all steps in this level in parallel
            tasks = []
            for step in level_steps:
                if step.condition and not self._evaluate_condition(step.condition, result):
                    continue
                
                task = self.execute_single_tool(step.tool_name, **step.parameters)
                tasks.append((step.step_id, task))
            
            # Wait for all tasks in this level
            if tasks:
                level_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
                
                for (step_id, _), step_result in zip(tasks, level_results):
                    if isinstance(step_result, Exception):
                        step_result = ToolResult(
                            success=False,
                            output=None,
                            error_message=str(step_result),
                            status=ToolStatus.FAILURE
                        )
                    
                    result.step_results[step_id] = step_result
                    if step_result.success:
                        result.completed_steps.append(step_id)
    
    async def _execute_conditional_chain(self, chain: ToolChain, result: ChainExecutionResult):
        """Execute chain with conditional logic"""
        
        # For now, treat as sequential with condition checking
        await self._execute_sequential_chain(chain, result)
    
    def _check_dependencies(self, step: ToolChainStep, result: ChainExecutionResult) -> bool:
        """Check if step dependencies are satisfied"""
        
        for dep_step_id in step.depends_on:
            if dep_step_id not in result.completed_steps:
                return False
        
        return True
    
    def _evaluate_condition(self, condition: str, result: ChainExecutionResult) -> bool:
        """Evaluate a condition string (simplified)"""
        
        # Simple condition evaluation
        # In production, this would be more sophisticated
        
        if "success" in condition.lower():
            # Check if previous steps were successful
            return all(step_result.success for step_result in result.step_results.values())
        elif "failure" in condition.lower():
            # Check if any previous step failed
            return any(not step_result.success for step_result in result.step_results.values())
        
        # Default to true
        return True
    
    def _group_by_dependencies(self, steps: List[ToolChainStep]) -> List[List[ToolChainStep]]:
        """Group steps by dependency levels for parallel execution"""
        
        levels = []
        remaining_steps = steps.copy()
        completed_step_ids = set()
        
        while remaining_steps:
            # Find steps with no unmet dependencies
            current_level = []
            
            for step in remaining_steps[:]:
                if all(dep in completed_step_ids for dep in step.depends_on):
                    current_level.append(step)
                    remaining_steps.remove(step)
            
            if not current_level:
                # Circular dependency or error - add remaining steps
                current_level = remaining_steps
                remaining_steps = []
            
            levels.append(current_level)
            completed_step_ids.update(step.step_id for step in current_level)
        
        return levels
    
    def optimize_tool_chain(self, chain: ToolChain) -> ToolChain:
        """Optimize tool chain for better performance"""
        
        # Simple optimizations
        optimized_steps = []
        
        for step in chain.steps:
            # Check if tool is available
            if tool_registry.get_tool(step.tool_name):
                optimized_steps.append(step)
            else:
                # Try to find alternative tool
                alternatives = self.route_task_to_tools(f"Alternative for {step.tool_name}")
                if alternatives:
                    step.tool_name = alternatives[0]
                    optimized_steps.append(step)
                    self.logger.info(f"Replaced unavailable tool with {alternatives[0]}")
        
        # Create optimized chain
        optimized_chain = ToolChain(
            chain_id=chain.chain_id + "_opt",
            name=chain.name + " (Optimized)",
            description=chain.description,
            steps=optimized_steps,
            strategy=chain.strategy,
            timeout=chain.timeout
        )
        
        return optimized_chain
    
    def get_chain_status(self, chain_id: str) -> Optional[Dict]:
        """Get status of a running chain"""
        
        if chain_id not in self.active_chains:
            return None
        
        result = self.active_chains[chain_id]
        
        return {
            "chain_id": chain_id,
            "success": result.success,
            "completed_steps": len(result.completed_steps),
            "total_steps": len(result.step_results),
            "execution_time": result.execution_time,
            "error_message": result.error_message,
            "step_details": {
                step_id: {
                    "success": step_result.success,
                    "execution_time": step_result.execution_time,
                    "error": step_result.error_message
                }
                for step_id, step_result in result.step_results.items()
            }
        }
    
    def cleanup_chain(self, chain_id: str) -> bool:
        """Clean up completed chain"""
        
        if chain_id in self.active_chains:
            del self.active_chains[chain_id]
            self.logger.info(f"Cleaned up chain {chain_id}")
            return True
        
        return False

# Global tool orchestrator instance
tool_orchestrator = ToolOrchestrator()
