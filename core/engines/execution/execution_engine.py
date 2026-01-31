"""
Execution Engine Integration - Main coordinator for tactical execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .tool_orchestrator import ToolOrchestrator, ToolChain, ChainExecutionResult
from .code_executor import CodeExecutor, CodeExecutionConfig
from .result_processor import ResultProcessor, ProcessedResult, DataType
from .recovery_system import RecoverySystem, RecoveryStrategy
from .parameter_mapper import parameter_mapper
from modules.tools.base_tool import ToolResult, tool_registry

@dataclass
class ExecutionRequest:
    request_id: str
    task_description: str
    tool_chain: Optional[ToolChain] = None
    single_tool: Optional[str] = None
    parameters: Dict[str, Any] = None
    validation_rules: Dict[str, Any] = None
    success_criteria: str = ""
    timeout: int = 300
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.validation_rules is None:
            self.validation_rules = {}

@dataclass
class ExecutionResult:
    request_id: str
    success: bool
    tool_results: Dict[str, ToolResult]
    processed_results: Dict[str, ProcessedResult]
    chain_result: Optional[ChainExecutionResult]
    execution_time: float
    recovery_attempts: int
    error_message: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ExecutionEngine:
    """Main execution engine that coordinates all tactical operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("execution_engine")
        
        # Initialize components
        self.tool_orchestrator = ToolOrchestrator()
        self.code_executor = CodeExecutor()
        self.result_processor = ResultProcessor()
        self.recovery_system = RecoverySystem()
        
        # Register code executor as a tool
        tool_registry.register_tool(self.code_executor)
        
        # State
        self.active_executions: Dict[str, ExecutionResult] = {}
        self.execution_history: List[ExecutionResult] = []
        
    async def execute_request(self, request: ExecutionRequest) -> ExecutionResult:
        """Main execution function - handle any execution request"""
        
        start_time = asyncio.get_event_loop().time()
        self.logger.info(f"Starting execution request: {request.request_id}")
        
        # Initialize result
        result = ExecutionResult(
            request_id=request.request_id,
            success=False,
            tool_results={},
            processed_results={},
            chain_result=None,
            execution_time=0.0,
            recovery_attempts=0
        )
        
        self.active_executions[request.request_id] = result
        
        try:
            if request.tool_chain:
                # Execute tool chain
                await self._execute_tool_chain(request, result)
            elif request.single_tool:
                # Execute single tool
                await self._execute_single_tool(request, result)
            else:
                # Auto-route based on task description
                await self._auto_execute_task(request, result)
            
            # Process results
            await self._process_results(request, result)
            
            # Validate success criteria
            if request.success_criteria:
                await self._validate_success_criteria(request, result)
            
            result.execution_time = asyncio.get_event_loop().time() - start_time
            
            # Determine overall success
            if result.chain_result:
                result.success = result.chain_result.success
            elif result.tool_results:
                result.success = all(tr.success for tr in result.tool_results.values())
            
            self.logger.info(f"Execution completed: {request.request_id}, success={result.success}")
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Execution failed: {request.request_id}, error={e}")
        
        # Store in history
        self.execution_history.append(result)
        
        # Cleanup active execution
        if request.request_id in self.active_executions:
            del self.active_executions[request.request_id]
        
        return result
    
    async def _execute_tool_chain(self, request: ExecutionRequest, result: ExecutionResult):
        """Execute a predefined tool chain"""
        
        self.logger.info(f"Executing tool chain: {request.tool_chain.chain_id}")
        
        # Execute chain with recovery
        chain_result = await self.recovery_system.execute_with_recovery(
            self.tool_orchestrator.execute_tool_chain,
            f"chain_{request.tool_chain.chain_id}",
            max_recovery_attempts=2,
            chain=request.tool_chain
        )
        
        if isinstance(chain_result, ChainExecutionResult):
            result.chain_result = chain_result
            result.tool_results = chain_result.step_results
        else:
            # Recovery system returned a ToolResult
            result.tool_results["chain_execution"] = chain_result
            result.chain_result = ChainExecutionResult(
                chain_id=request.tool_chain.chain_id,
                success=chain_result.success,
                step_results={"main": chain_result},
                execution_time=chain_result.execution_time,
                error_message=chain_result.error_message
            )
    
    async def _execute_single_tool(self, request: ExecutionRequest, result: ExecutionResult):
        """Execute a single tool"""
        
        self.logger.info(f"Executing single tool: {request.single_tool}")
        
        # Map parameters for the specific tool
        mapped_params = parameter_mapper.map_parameters(request.single_tool, request.parameters)
        
        # Execute tool with recovery
        async def execute_tool_wrapper(**kwargs):
            return await self.tool_orchestrator.execute_single_tool(request.single_tool, **kwargs)
        
        tool_result = await self.recovery_system.execute_with_recovery(
            execute_tool_wrapper,
            request.single_tool,
            max_recovery_attempts=3,
            **mapped_params
        )
        
        result.tool_results[request.single_tool] = tool_result
    
    async def _auto_execute_task(self, request: ExecutionRequest, result: ExecutionResult):
        """Auto-route task to appropriate tools"""
        
        self.logger.info(f"Auto-routing task: {request.task_description}")
        
        # Route to tools
        suggested_tools = self.tool_orchestrator.route_task_to_tools(request.task_description)
        
        if len(suggested_tools) == 1:
            # Single tool execution
            tool_name = suggested_tools[0]
            
            # Map parameters for the specific tool
            mapped_params = parameter_mapper.map_parameters(tool_name, request.parameters)
            
            async def execute_tool_wrapper(**kwargs):
                return await self.tool_orchestrator.execute_single_tool(tool_name, **kwargs)
            
            tool_result = await self.recovery_system.execute_with_recovery(
                execute_tool_wrapper,
                tool_name,
                max_recovery_attempts=3,
                **mapped_params
            )
            result.tool_results[tool_name] = tool_result
            
        else:
            # Create simple sequential chain
            chain_steps = []
            for i, tool_name in enumerate(suggested_tools):
                # Map parameters for each tool in the chain
                mapped_params = parameter_mapper.map_parameters(tool_name, request.parameters)
                
                step_data = {
                    "tool": tool_name,
                    "parameters": mapped_params,
                    "depends_on": [f"step_{i:02d}"] if i > 0 else []
                }
                chain_steps.append(step_data)
            
            # Create and execute chain
            chain = self.tool_orchestrator.create_tool_chain(request.task_description, chain_steps)
            chain_result = await self.tool_orchestrator.execute_tool_chain(chain)
            
            result.chain_result = chain_result
            result.tool_results = chain_result.step_results
    
    async def _process_results(self, request: ExecutionRequest, result: ExecutionResult):
        """Process all tool results"""
        
        self.logger.info("Processing execution results")
        
        for tool_name, tool_result in result.tool_results.items():
            # Process result
            processed = self.result_processor.process_result(
                tool_result,
                validation_rules=request.validation_rules
            )
            
            result.processed_results[tool_name] = processed
            
            # Extract specific data if configured
            if "extraction_config" in request.parameters:
                extracted = self.result_processor.extract_specific_data(
                    processed,
                    request.parameters["extraction_config"]
                )
                processed.extracted_values.update(extracted)
    
    async def _validate_success_criteria(self, request: ExecutionRequest, result: ExecutionResult):
        """Validate if execution meets success criteria"""
        
        self.logger.info("Validating success criteria")
        
        success_count = 0
        total_count = len(result.processed_results)
        
        for tool_name, processed_result in result.processed_results.items():
            is_success, message = self.result_processor.validate_success_criteria(
                processed_result,
                request.success_criteria
            )
            
            if is_success:
                success_count += 1
            else:
                self.logger.warning(f"Success criteria not met for {tool_name}: {message}")
        
        # Overall success if majority of tools meet criteria
        criteria_met = success_count >= (total_count / 2)
        
        if not criteria_met:
            result.error_message = f"Success criteria not met: {success_count}/{total_count} tools passed"
    
    async def execute_code(self, code: str, language: str = "python", 
                          config: Optional[CodeExecutionConfig] = None) -> ExecutionResult:
        """Execute code directly"""
        
        request_id = f"code_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Map parameters for code executor
        params = {"code": code, "language": language}
        if config:
            params["config"] = config
        
        mapped_params = parameter_mapper.map_parameters("code_executor", params)
        
        request = ExecutionRequest(
            request_id=request_id,
            task_description=f"Execute {language} code",
            single_tool="code_executor",
            parameters=mapped_params
        )
        
        return await self.execute_request(request)
    
    async def execute_workflow_step(self, step_description: str, tools_required: List[str],
                                  parameters: Dict[str, Any], success_criteria: str = "") -> ExecutionResult:
        """Execute a workflow step with specific tools"""
        
        request_id = f"workflow_step_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create tool chain for the step
        chain_steps = []
        for i, tool_name in enumerate(tools_required):
            step_data = {
                "tool": tool_name,
                "parameters": parameters.get(tool_name, {}),
                "depends_on": [f"step_{i:02d}"] if i > 0 else []
            }
            chain_steps.append(step_data)
        
        chain = self.tool_orchestrator.create_tool_chain(step_description, chain_steps)
        
        request = ExecutionRequest(
            request_id=request_id,
            task_description=step_description,
            tool_chain=chain,
            success_criteria=success_criteria
        )
        
        return await self.execute_request(request)
    
    def get_execution_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active execution"""
        
        if request_id not in self.active_executions:
            return None
        
        result = self.active_executions[request_id]
        
        return {
            "request_id": request_id,
            "success": result.success,
            "execution_time": result.execution_time,
            "tools_executed": len(result.tool_results),
            "tools_processed": len(result.processed_results),
            "recovery_attempts": result.recovery_attempts,
            "error_message": result.error_message,
            "chain_status": self.tool_orchestrator.get_chain_status(
                result.chain_result.chain_id
            ) if result.chain_result else None
        }
    
    def get_execution_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get execution summary for the time window"""
        
        current_time = asyncio.get_event_loop().time()
        recent_executions = [
            ex for ex in self.execution_history
            if current_time - ex.execution_time <= time_window
        ]
        
        if not recent_executions:
            return {"total_executions": 0}
        
        successful = [ex for ex in recent_executions if ex.success]
        failed = [ex for ex in recent_executions if not ex.success]
        
        avg_execution_time = sum(ex.execution_time for ex in recent_executions) / len(recent_executions)
        
        # Tool usage statistics
        tool_usage = {}
        for execution in recent_executions:
            for tool_name in execution.tool_results.keys():
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        return {
            "total_executions": len(recent_executions),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": len(successful) / len(recent_executions),
            "average_execution_time": avg_execution_time,
            "tool_usage": tool_usage,
            "recovery_attempts": sum(ex.recovery_attempts for ex in recent_executions),
            "time_window_hours": time_window / 3600
        }
    
    def optimize_execution(self, request: ExecutionRequest) -> ExecutionRequest:
        """Optimize execution request based on historical data"""
        
        # Simple optimization based on tool success rates
        if request.tool_chain:
            optimized_chain = self.tool_orchestrator.optimize_tool_chain(request.tool_chain)
            request.tool_chain = optimized_chain
        
        # Adjust timeout based on historical execution times
        recent_executions = self.execution_history[-10:]  # Last 10 executions
        if recent_executions:
            avg_time = sum(ex.execution_time for ex in recent_executions) / len(recent_executions)
            # Set timeout to 3x average time, minimum 60 seconds
            request.timeout = max(60, int(avg_time * 3))
        
        return request

# Global execution engine instance
execution_engine = ExecutionEngine()
