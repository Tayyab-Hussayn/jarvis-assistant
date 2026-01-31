#!/usr/bin/env python3
"""
Enhanced Workflow Engine - Temporal.io integration with fallback to simple engine
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import uuid

# Import both engines
from .simple_workflow import SimpleWorkflowEngine, SimpleWorkflow, WorkflowStep, WorkflowStatus

# Import Temporal components with fallback
try:
    from core.workflows.temporal_engine import TemporalWorkflowEngine, WorkflowRequest, WorkflowResult
    from core.workflows.jarvis_workflows import workflow_manager
    TEMPORAL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Temporal components not available: {e}")
    # Create mock classes for fallback
    class MockTemporalEngine:
        async def initialize(self): return False
        async def execute_workflow(self, request): return {"success": False, "error": "Temporal not available"}
        async def get_workflow_status(self, wf_id): return {"status": "error"}
        async def cancel_workflow(self, wf_id): return False
        async def list_workflows(self): return []
        async def close(self): pass
    
    class MockWorkflowManager:
        async def initialize(self): return False
        async def create_simple_task(self, *args, **kwargs): return "mock_id"
        async def create_multi_step_task(self, *args, **kwargs): return "mock_id"
        async def create_approval_task(self, *args, **kwargs): return "mock_id"
    
    TemporalWorkflowEngine = MockTemporalEngine
    workflow_manager = MockWorkflowManager()
    TEMPORAL_AVAILABLE = False

@dataclass
class EnhancedWorkflowRequest:
    """Enhanced workflow request supporting both engines"""
    workflow_id: Optional[str] = None
    name: str = ""
    description: str = ""
    workflow_type: str = "simple"  # "simple", "temporal_simple", "temporal_multi", "temporal_approval"
    steps: List[Dict[str, Any]] = None
    parameters: Dict[str, Any] = None
    use_temporal: bool = True
    timeout_minutes: int = 60
    
    def __post_init__(self):
        if self.workflow_id is None:
            self.workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        if self.steps is None:
            self.steps = []
        if self.parameters is None:
            self.parameters = {}

class EnhancedWorkflowEngine:
    """Enhanced workflow engine with Temporal.io integration and fallback"""
    
    def __init__(self):
        self.temporal_engine = TemporalWorkflowEngine()
        self.simple_engine = SimpleWorkflowEngine()
        self.logger = logging.getLogger("enhanced_workflow")
        
        # Engine status
        self.temporal_available = False
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize both engines"""
        try:
            # Try to initialize Temporal
            self.temporal_available = await self.temporal_engine.initialize()
            
            if self.temporal_available:
                # Initialize workflow manager
                await workflow_manager.initialize()
                self.logger.info("✅ Temporal.io engine initialized")
            else:
                self.logger.warning("⚠️ Temporal.io not available, using simple engine only")
            
            # Simple engine is always available
            self.initialized = True
            self.logger.info("✅ Enhanced workflow engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced workflow engine initialization failed: {e}")
            self.initialized = False
            return False
    
    async def execute_workflow(self, request: EnhancedWorkflowRequest) -> Dict[str, Any]:
        """Execute workflow using appropriate engine"""
        
        if not self.initialized:
            await self.initialize()
        
        # Determine which engine to use
        use_temporal = request.use_temporal and self.temporal_available
        
        if use_temporal:
            return await self._execute_temporal_workflow(request)
        else:
            return await self._execute_simple_workflow(request)
    
    async def _execute_temporal_workflow(self, request: EnhancedWorkflowRequest) -> Dict[str, Any]:
        """Execute workflow using Temporal.io"""
        
        try:
            if request.workflow_type == "temporal_simple":
                # Simple single-task workflow
                tool_name = request.parameters.get("tool_name", "terminal")
                tool_params = {k: v for k, v in request.parameters.items() if k != "tool_name"}
                
                workflow_id = await workflow_manager.create_simple_task(
                    task_description=request.description,
                    tool_name=tool_name,
                    **tool_params
                )
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "engine": "temporal",
                    "type": "simple_task",
                    "status": "started"
                }
            
            elif request.workflow_type == "temporal_multi":
                # Multi-step workflow
                workflow_id = await workflow_manager.create_multi_step_task(
                    task_description=request.description,
                    steps=request.steps
                )
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "engine": "temporal",
                    "type": "multi_step",
                    "status": "started",
                    "steps_count": len(request.steps)
                }
            
            elif request.workflow_type == "temporal_approval":
                # Approval workflow
                tool_name = request.parameters.get("tool_name", "terminal")
                approval_message = request.parameters.get("approval_message", "Approve this task?")
                tool_params = {k: v for k, v in request.parameters.items() 
                             if k not in ["tool_name", "approval_message"]}
                
                workflow_id = await workflow_manager.create_approval_task(
                    task_description=request.description,
                    approval_message=approval_message,
                    tool_name=tool_name,
                    **tool_params
                )
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "engine": "temporal",
                    "type": "approval",
                    "status": "waiting_approval"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown Temporal workflow type: {request.workflow_type}",
                    "engine": "temporal"
                }
                
        except Exception as e:
            self.logger.error(f"Temporal workflow execution failed: {e}")
            # Fallback to simple engine
            self.logger.info("Falling back to simple workflow engine")
            return await self._execute_simple_workflow(request)
    
    async def _execute_simple_workflow(self, request: EnhancedWorkflowRequest) -> Dict[str, Any]:
        """Execute workflow using simple engine"""
        
        try:
            # Convert enhanced request to simple workflow
            workflow_steps = []
            
            if request.steps:
                # Multi-step workflow
                for i, step in enumerate(request.steps):
                    step_id = step.get("id", f"step_{i+1}")
                    workflow_steps.append(WorkflowStep(
                        id=step_id,
                        name=step.get("name", f"Step {i+1}"),
                        tool=step.get("tool", "terminal"),
                        parameters=step.get("parameters", {}),
                        depends_on=step.get("depends_on", [])
                    ))
            else:
                # Single-step workflow
                tool_name = request.parameters.get("tool_name", "terminal")
                tool_params = {k: v for k, v in request.parameters.items() if k != "tool_name"}
                
                workflow_steps.append(WorkflowStep(
                    id="main_step",
                    name=request.name or "Main Task",
                    tool=tool_name,
                    parameters=tool_params
                ))
            
            # Create simple workflow
            simple_workflow = SimpleWorkflow(
                id=request.workflow_id,
                name=request.name,
                steps=workflow_steps
            )
            
            # Execute workflow
            result = await self.simple_engine.execute_workflow(simple_workflow)
            
            return {
                "success": result.get("success", False),
                "workflow_id": request.workflow_id,
                "engine": "simple",
                "result": result,
                "status": "completed" if result.get("success") else "failed"
            }
            
        except Exception as e:
            self.logger.error(f"Simple workflow execution failed: {e}")
            return {
                "success": False,
                "workflow_id": request.workflow_id,
                "engine": "simple",
                "error": str(e),
                "status": "failed"
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status from appropriate engine"""
        
        # Try Temporal first if available
        if self.temporal_available:
            temporal_status = await self.temporal_engine.get_workflow_status(workflow_id)
            if temporal_status.get("status") != "error":
                return {
                    "workflow_id": workflow_id,
                    "engine": "temporal",
                    **temporal_status
                }
        
        # Check simple engine
        simple_status = self.simple_engine.get_workflow_status(workflow_id)
        if simple_status:
            return {
                "workflow_id": workflow_id,
                "engine": "simple",
                "status": simple_status.status.value,
                "state": simple_status.state
            }
        
        return {
            "workflow_id": workflow_id,
            "status": "not_found",
            "error": "Workflow not found in any engine"
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow in appropriate engine"""
        
        # Try Temporal first
        if self.temporal_available:
            if await self.temporal_engine.cancel_workflow(workflow_id):
                return True
        
        # Try simple engine
        return self.simple_engine.cancel_workflow(workflow_id)
    
    async def list_workflows(self, engine: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflows from specified engine or both"""
        
        workflows = []
        
        if engine != "simple" and self.temporal_available:
            temporal_workflows = await self.temporal_engine.list_workflows()
            for wf in temporal_workflows:
                workflows.append({
                    "engine": "temporal",
                    **wf
                })
        
        if engine != "temporal":
            simple_workflows = self.simple_engine.list_workflows()
            for wf in simple_workflows:
                workflows.append({
                    "engine": "simple",
                    "workflow_id": wf.id,
                    "name": wf.name,
                    "status": wf.status.value,
                    "steps_count": len(wf.steps)
                })
        
        return workflows
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of both engines"""
        return {
            "initialized": self.initialized,
            "temporal_available": self.temporal_available,
            "simple_available": True,
            "preferred_engine": "temporal" if self.temporal_available else "simple"
        }
    
    async def close(self):
        """Close all engines"""
        if self.temporal_available:
            await self.temporal_engine.close()
        # Simple engine doesn't need explicit closing

# Global enhanced workflow engine
enhanced_workflow_engine = EnhancedWorkflowEngine()
