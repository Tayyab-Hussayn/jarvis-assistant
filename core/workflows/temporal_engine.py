#!/usr/bin/env python3
"""
Temporal Workflow Engine - Enterprise-grade workflow management for JARVIS
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

# Temporal imports
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy

@dataclass
class WorkflowRequest:
    """Workflow execution request"""
    workflow_id: str
    workflow_type: str
    input_data: Dict[str, Any]
    schedule: Optional[str] = None
    timeout: Optional[timedelta] = None

@dataclass
class WorkflowResult:
    """Workflow execution result"""
    workflow_id: str
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time: float = 0
    status: str = "completed"

class TemporalWorkflowEngine:
    """Enterprise workflow engine using Temporal.io"""
    
    def __init__(self, temporal_address: str = "localhost:7233"):
        self.temporal_address = temporal_address
        self.client: Optional[Client] = None
        self.worker: Optional[Worker] = None
        self.logger = logging.getLogger("temporal_engine")
        
        # Workflow registry
        self.registered_workflows = {}
        self.registered_activities = {}
        
        # Connection status
        self.connected = False
    
    async def initialize(self) -> bool:
        """Initialize Temporal client and worker"""
        try:
            # Connect to Temporal server
            self.client = await Client.connect(self.temporal_address)
            
            # Create worker
            self.worker = Worker(
                self.client,
                task_queue="jarvis-task-queue",
                workflows=[],  # Will be populated dynamically
                activities=[]  # Will be populated dynamically
            )
            
            self.connected = True
            self.logger.info("✅ Temporal.io connected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Temporal.io connection failed: {e}")
            self.connected = False
            return False
    
    async def start_worker(self):
        """Start Temporal worker"""
        if not self.connected:
            await self.initialize()
        
        if self.worker:
            self.logger.info("🔄 Starting Temporal worker...")
            await self.worker.run()
    
    async def execute_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """Execute a workflow"""
        if not self.connected:
            return WorkflowResult(
                workflow_id=request.workflow_id,
                success=False,
                result=None,
                error_message="Temporal not connected"
            )
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Start workflow
            handle = await self.client.start_workflow(
                request.workflow_type,
                request.input_data,
                id=request.workflow_id,
                task_queue="jarvis-task-queue",
                execution_timeout=request.timeout or timedelta(hours=24)
            )
            
            # Wait for result
            result = await handle.result()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return WorkflowResult(
                workflow_id=request.workflow_id,
                success=True,
                result=result,
                execution_time=execution_time,
                status="completed"
            )
            
        except Exception as e:
            return WorkflowResult(
                workflow_id=request.workflow_id,
                success=False,
                result=None,
                error_message=str(e),
                status="failed"
            )
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        if not self.connected:
            return {"status": "temporal_not_connected"}
        
        try:
            handle = self.client.get_workflow_handle(workflow_id)
            
            # Get workflow info
            description = await handle.describe()
            
            return {
                "workflow_id": workflow_id,
                "status": description.status.name,
                "start_time": description.start_time,
                "execution_time": description.execution_time,
                "run_id": description.run_id
            }
            
        except Exception as e:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if not self.connected:
            return False
        
        try:
            handle = self.client.get_workflow_handle(workflow_id)
            await handle.cancel()
            self.logger.info(f"Cancelled workflow: {workflow_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            return False
    
    async def list_workflows(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflows with optional status filter"""
        if not self.connected:
            return []
        
        try:
            # This would use Temporal's list workflows API
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            self.logger.error(f"Failed to list workflows: {e}")
            return []
    
    def register_workflow(self, workflow_class):
        """Register a workflow class"""
        workflow_name = workflow_class.__name__
        self.registered_workflows[workflow_name] = workflow_class
        self.logger.info(f"Registered workflow: {workflow_name}")
    
    def register_activity(self, activity_func):
        """Register an activity function"""
        activity_name = activity_func.__name__
        self.registered_activities[activity_name] = activity_func
        self.logger.info(f"Registered activity: {activity_name}")
    
    async def close(self):
        """Close Temporal connections"""
        if self.client:
            await self.client.close()
        self.connected = False
        self.logger.info("Temporal connections closed")

# Global Temporal workflow engine
temporal_engine = TemporalWorkflowEngine()
