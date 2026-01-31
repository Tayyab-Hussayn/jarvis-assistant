"""
Simple Workflow Engine - Lightweight workflow execution
"""

import asyncio
import json
from typing import Dict, List, Any
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
    
    async def execute_workflow(self, workflow: SimpleWorkflow) -> bool:
        """Execute workflow steps"""
        workflow.status = WorkflowStatus.RUNNING
        
        for step in workflow.steps:
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
            else:
                workflow.state[step.id] = True
        
        workflow.status = WorkflowStatus.COMPLETED
        return True

# Global workflow engine
workflow_engine = SimpleWorkflowEngine()
