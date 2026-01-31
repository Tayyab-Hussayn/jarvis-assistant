"""
Simple Workflow Engine - Lightweight workflow execution
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class WorkflowStep:
    id: str
    name: str
    tool: str
    parameters: Dict[str, Any]
    depends_on: List[str] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

@dataclass
class SimpleWorkflow:
    id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    state: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.state is None:
            self.state = {}

class SimpleWorkflowEngine:
    """Lightweight workflow engine"""
    
    def __init__(self):
        self.workflows: Dict[str, SimpleWorkflow] = {}
        self.execution_engine = None
        
    def set_execution_engine(self, engine):
        self.execution_engine = engine
    
    def create_workflow_from_nl(self, description: str) -> SimpleWorkflow:
        """Create workflow from natural language"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Simple NL to workflow conversion
        steps = []
        if "calculate" in description.lower():
            steps.append(WorkflowStep("calc", "Calculate", "calculator", {"expression": "2+2"}))
        if "file" in description.lower():
            steps.append(WorkflowStep("file", "File Operation", "file_manager", {"operation": "create_dir", "path": "/tmp/test"}))
        
        if not steps:
            steps.append(WorkflowStep("default", "Default Task", "human_input", {"prompt": description}))
        
        return SimpleWorkflow(workflow_id, description, steps)
    
    async def execute_workflow(self, workflow: SimpleWorkflow) -> Dict[str, Any]:
        """Execute workflow steps"""
        workflow.status = WorkflowStatus.RUNNING
        self.workflows[workflow.id] = workflow
        
        results = {}
        
        for step in workflow.steps:
            try:
                if self.execution_engine:
                    from core.engines.execution.execution_engine import ExecutionRequest
                    request = ExecutionRequest(
                        request_id=f"{workflow.id}_{step.id}",
                        task_description=step.name,
                        single_tool=step.tool,
                        parameters=step.parameters
                    )
                    result = await self.execution_engine.execute_request(request)
                    workflow.state[step.id] = result.success
                    results[step.id] = {
                        "success": result.success,
                        "output": getattr(result, 'output', None),
                        "error": getattr(result, 'error_message', None)
                    }
                else:
                    # Mock execution for testing
                    workflow.state[step.id] = True
                    results[step.id] = {
                        "success": True,
                        "output": f"Mock execution of {step.tool}",
                        "error": None
                    }
            except Exception as e:
                workflow.state[step.id] = False
                results[step.id] = {
                    "success": False,
                    "output": None,
                    "error": str(e)
                }
        
        # Determine overall success
        all_success = all(workflow.state.values())
        workflow.status = WorkflowStatus.COMPLETED if all_success else WorkflowStatus.FAILED
        
        return {
            "success": all_success,
            "workflow_id": workflow.id,
            "results": results,
            "status": workflow.status.value
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[SimpleWorkflow]:
        """Get workflow status"""
        return self.workflows.get(workflow_id)
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].status = WorkflowStatus.FAILED
            return True
        return False
    
    def list_workflows(self) -> List[SimpleWorkflow]:
        """List all workflows"""
        return list(self.workflows.values())

# Global workflow engine
workflow_engine = SimpleWorkflowEngine()
