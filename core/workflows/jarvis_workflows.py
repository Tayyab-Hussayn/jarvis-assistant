#!/usr/bin/env python3
"""
JARVIS Temporal Workflows - Pre-built workflow patterns
"""

import asyncio
from datetime import timedelta
from typing import Dict, List, Any, Optional

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

# Import JARVIS components
import sys
import logging
import uuid
sys.path.append('/home/krawin/exp.code/jarvis')

try:
    from modules.tools.base_tool import tool_registry
    from core.llm.llm_manager import llm_manager
except ImportError as e:
    print(f"Warning: Could not import JARVIS components: {e}")
    # Create mock objects for testing
    class MockToolRegistry:
        async def execute_tool(self, tool_name, **params):
            return type('Result', (), {
                'success': True,
                'output': f"Mock execution of {tool_name}",
                'error_message': None,
                'execution_time': 0.1
            })()
    
    class MockLLMManager:
        async def generate(self, prompt, system_prompt=None, provider=None):
            return type('Response', (), {
                'content': f"Mock LLM response to: {prompt[:50]}...",
                'model': 'mock-model',
                'provider': 'mock',
                'tokens_used': 100
            })()
    
    tool_registry = MockToolRegistry()
    llm_manager = MockLLMManager()

from .temporal_engine import TemporalWorkflowEngine, WorkflowRequest, WorkflowResult

# Activity Definitions
@activity.defn
async def execute_tool_activity(tool_name: str, **parameters) -> Dict[str, Any]:
    """Execute a JARVIS tool as Temporal activity"""
    try:
        result = await tool_registry.execute_tool(tool_name, **parameters)
        return {
            "success": result.success,
            "output": result.output,
            "error_message": result.error_message,
            "execution_time": getattr(result, 'execution_time', 0)
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error_message": str(e),
            "execution_time": 0
        }

@activity.defn
async def llm_reasoning_activity(prompt: str, system_prompt: Optional[str] = None, 
                               provider: Optional[str] = None) -> Dict[str, Any]:
    """Execute LLM reasoning as Temporal activity"""
    try:
        response = await llm_manager.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=provider
        )
        return {
            "success": True,
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_used": response.tokens_used
        }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": str(e)
        }

@activity.defn
async def wait_for_approval_activity(message: str, timeout_minutes: int = 60) -> Dict[str, Any]:
    """Wait for human approval as Temporal activity"""
    try:
        # In real implementation, this would integrate with notification system
        print(f"⏳ Waiting for approval: {message}")
        
        # For now, simulate approval after short delay
        await asyncio.sleep(2)
        
        return {
            "approved": True,
            "message": "Auto-approved for demo",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "approved": False,
            "error": str(e)
        }

# Workflow Definitions
@workflow.defn
class SimpleTaskWorkflow:
    """Simple single-task workflow"""
    
    @workflow.run
    async def run(self, task_description: str, tool_name: str, **parameters) -> Dict[str, Any]:
        """Execute a simple task workflow"""
        
        # Step 1: Reason about the task
        reasoning_result = await workflow.execute_activity(
            llm_reasoning_activity,
            f"Analyze this task: {task_description}. Provide brief analysis.",
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        if not reasoning_result["success"]:
            return {"success": False, "error": "Reasoning failed"}
        
        # Step 2: Execute the tool
        tool_result = await workflow.execute_activity(
            execute_tool_activity,
            tool_name,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            **parameters
        )
        
        return {
            "success": tool_result["success"],
            "reasoning": reasoning_result["content"],
            "tool_result": tool_result,
            "workflow_id": workflow.info().workflow_id
        }

@workflow.defn
class MultiStepTaskWorkflow:
    """Multi-step task workflow with dependencies"""
    
    @workflow.run
    async def run(self, task_description: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multi-step workflow"""
        
        workflow_results = []
        
        # Step 1: Initial reasoning
        initial_reasoning = await workflow.execute_activity(
            llm_reasoning_activity,
            f"Plan execution for: {task_description}. Break down the approach.",
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        workflow_results.append({
            "step": "initial_reasoning",
            "result": initial_reasoning
        })
        
        # Execute each step
        for i, step in enumerate(steps):
            step_name = step.get("name", f"step_{i+1}")
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            
            # Execute step
            step_result = await workflow.execute_activity(
                execute_tool_activity,
                tool_name,
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=RetryPolicy(maximum_attempts=3),
                **parameters
            )
            
            workflow_results.append({
                "step": step_name,
                "tool": tool_name,
                "result": step_result
            })
            
            # If step failed and marked as critical, stop workflow
            if not step_result["success"] and step.get("critical", False):
                return {
                    "success": False,
                    "error": f"Critical step {step_name} failed",
                    "completed_steps": workflow_results
                }
        
        # Final reasoning about results
        final_reasoning = await workflow.execute_activity(
            llm_reasoning_activity,
            f"Analyze the results of this workflow: {task_description}. Summarize outcomes.",
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        workflow_results.append({
            "step": "final_analysis",
            "result": final_reasoning
        })
        
        return {
            "success": True,
            "workflow_id": workflow.info().workflow_id,
            "task_description": task_description,
            "steps_completed": len(steps),
            "results": workflow_results
        }

@workflow.defn
class ApprovalWorkflow:
    """Workflow requiring human approval"""
    
    @workflow.run
    async def run(self, task_description: str, approval_message: str, 
                 tool_name: str, **parameters) -> Dict[str, Any]:
        """Execute workflow with approval gate"""
        
        # Step 1: Request approval
        approval_result = await workflow.execute_activity(
            wait_for_approval_activity,
            approval_message,
            start_to_close_timeout=timedelta(hours=24),  # Long timeout for human response
            retry_policy=RetryPolicy(maximum_attempts=1)
        )
        
        if not approval_result["approved"]:
            return {
                "success": False,
                "error": "Approval denied or timed out",
                "approval_result": approval_result
            }
        
        # Step 2: Execute approved task
        tool_result = await workflow.execute_activity(
            execute_tool_activity,
            tool_name,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
            **parameters
        )
        
        return {
            "success": tool_result["success"],
            "approval": approval_result,
            "execution": tool_result,
            "workflow_id": workflow.info().workflow_id
        }

@workflow.defn
class ScheduledTaskWorkflow:
    """Scheduled recurring task workflow"""
    
    @workflow.run
    async def run(self, task_description: str, tool_name: str, 
                 schedule_interval: int, max_iterations: int = 10, 
                 **parameters) -> Dict[str, Any]:
        """Execute scheduled recurring workflow"""
        
        results = []
        
        for iteration in range(max_iterations):
            # Wait for scheduled interval (except first iteration)
            if iteration > 0:
                await asyncio.sleep(schedule_interval)
            
            # Execute scheduled task
            task_result = await workflow.execute_activity(
                execute_tool_activity,
                tool_name,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=2),
                **parameters
            )
            
            results.append({
                "iteration": iteration + 1,
                "timestamp": asyncio.get_event_loop().time(),
                "result": task_result
            })
            
            # If task fails multiple times, stop scheduling
            recent_failures = sum(1 for r in results[-3:] if not r["result"]["success"])
            if recent_failures >= 3:
                return {
                    "success": False,
                    "error": "Too many consecutive failures",
                    "iterations_completed": iteration + 1,
                    "results": results
                }
        
        return {
            "success": True,
            "workflow_id": workflow.info().workflow_id,
            "iterations_completed": max_iterations,
            "results": results
        }

class TemporalWorkflowManager:
    """High-level workflow management interface"""
    
    def __init__(self):
        self.engine = TemporalWorkflowEngine()
        self.logger = logging.getLogger("workflow_manager")
    
    async def initialize(self) -> bool:
        """Initialize workflow manager"""
        return await self.engine.initialize()
    
    async def create_simple_task(self, task_description: str, tool_name: str, 
                               **parameters) -> str:
        """Create and start simple task workflow"""
        
        workflow_id = f"simple_task_{uuid.uuid4().hex[:8]}"
        
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="SimpleTaskWorkflow",
            input_data={
                "task_description": task_description,
                "tool_name": tool_name,
                **parameters
            }
        )
        
        result = await self.engine.execute_workflow(request)
        
        if result.success:
            self.logger.info(f"✅ Simple task workflow started: {workflow_id}")
        else:
            self.logger.error(f"❌ Simple task workflow failed: {result.error_message}")
        
        return workflow_id
    
    async def create_multi_step_task(self, task_description: str, 
                                   steps: List[Dict[str, Any]]) -> str:
        """Create and start multi-step workflow"""
        
        workflow_id = f"multi_step_{uuid.uuid4().hex[:8]}"
        
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="MultiStepTaskWorkflow",
            input_data={
                "task_description": task_description,
                "steps": steps
            }
        )
        
        result = await self.engine.execute_workflow(request)
        
        if result.success:
            self.logger.info(f"✅ Multi-step workflow started: {workflow_id}")
        else:
            self.logger.error(f"❌ Multi-step workflow failed: {result.error_message}")
        
        return workflow_id
    
    async def create_approval_task(self, task_description: str, approval_message: str,
                                 tool_name: str, **parameters) -> str:
        """Create workflow requiring approval"""
        
        workflow_id = f"approval_{uuid.uuid4().hex[:8]}"
        
        request = WorkflowRequest(
            workflow_id=workflow_id,
            workflow_type="ApprovalWorkflow",
            input_data={
                "task_description": task_description,
                "approval_message": approval_message,
                "tool_name": tool_name,
                **parameters
            }
        )
        
        result = await self.engine.execute_workflow(request)
        
        if result.success:
            self.logger.info(f"✅ Approval workflow started: {workflow_id}")
        else:
            self.logger.error(f"❌ Approval workflow failed: {result.error_message}")
        
        return workflow_id
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        return await self.engine.get_workflow_status(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow"""
        return await self.engine.cancel_workflow(workflow_id)

# Global workflow manager
workflow_manager = TemporalWorkflowManager()
