"""
Simple Workflow Engine - Lightweight workflow execution
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .multi_task_parser import TaskInfo

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
    description: str = ""  # Add description field
    
    def __post_init__(self):
        if self.state is None:
            self.state = {}
        if not self.description:
            self.description = self.name  # Use name as description if not provided
            self.state = {}

class SimpleWorkflowEngine:
    """Lightweight workflow engine"""
    
    def __init__(self):
        self.workflows: Dict[str, SimpleWorkflow] = {}
        self.execution_engine = None
        self.logger = logging.getLogger("simple_workflow")
        
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
        
        return SimpleWorkflow(workflow_id, description, steps, description=description)
    
    async def execute_workflow(self, workflow: SimpleWorkflow) -> Dict[str, Any]:
        """Execute workflow steps with intelligent multi-task handling"""
        workflow.status = WorkflowStatus.RUNNING
        self.workflows[workflow.id] = workflow
        
        results = {}
        
        # Check if this is a multi-task workflow
        from .multi_task_parser import multi_task_parser
        
        task_infos = multi_task_parser.parse_workflow_description(workflow.description)
        
        if len(task_infos) > 1:
            self.logger.info(f"🔄 Multi-task workflow detected: {len(task_infos)} tasks")
            return await self._execute_multi_task_workflow(workflow, task_infos)
        else:
            self.logger.info(f"📝 Single task workflow: {task_infos[0].project_name}")
            return await self._execute_single_task_workflow(workflow, task_infos[0])
    
    async def _execute_multi_task_workflow(self, workflow: SimpleWorkflow, task_infos: List) -> Dict[str, Any]:
        """Execute multi-task workflow with intelligent organization"""
        
        results = {'tasks': {}, 'summary': {}}
        
        for i, task_info in enumerate(task_infos):
            self.logger.info(f"🎯 Starting Task {i+1}/{len(task_infos)}: {task_info.project_name}")
            
            try:
                # Execute individual task
                task_result = await self._execute_individual_task(task_info)
                
                results['tasks'][task_info.id] = {
                    'project_name': task_info.project_name,
                    'folder': task_info.folder_name,
                    'status': 'completed' if task_result['success'] else 'failed',
                    'files_created': task_result.get('files_created', []),
                    'result': task_result
                }
                
                self.logger.info(f"✅ Task {i+1} completed: {task_info.project_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Task {i+1} failed: {e}")
                results['tasks'][task_info.id] = {
                    'project_name': task_info.project_name,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Generate summary
        completed_tasks = len([t for t in results['tasks'].values() if t['status'] == 'completed'])
        results['summary'] = {
            'total_tasks': len(task_infos),
            'completed': completed_tasks,
            'failed': len(task_infos) - completed_tasks,
            'success_rate': f"{(completed_tasks/len(task_infos)*100):.1f}%"
        }
        
        workflow.status = WorkflowStatus.COMPLETED
        self.logger.info(f"🎉 Multi-task workflow completed: {completed_tasks}/{len(task_infos)} tasks successful")
        
        return {
            "workflow_id": workflow.id,
            "status": "completed",
            "results": results,
            "success": completed_tasks > 0
        }
    
    async def _execute_single_task_workflow(self, workflow: SimpleWorkflow, task_info) -> Dict[str, Any]:
        """Execute single task workflow with organization"""
        
        try:
            task_result = await self._execute_individual_task(task_info)
            
            workflow.status = WorkflowStatus.COMPLETED
            
            return {
                "workflow_id": workflow.id,
                "status": "completed",
                "results": {
                    'project_name': task_info.project_name,
                    'folder': task_info.folder_name,
                    'files_created': task_result.get('files_created', []),
                    'task_result': task_result
                },
                "success": task_result['success']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Single task workflow failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            
            return {
                "workflow_id": workflow.id,
                "status": "failed",
                "error": str(e),
                "success": False
            }
    
    async def _execute_individual_task(self, task_info) -> Dict[str, Any]:
        """Execute individual task with intelligent file organization"""
        
        try:
            # Use LLM for content generation
            from core.llm.llm_manager import llm_manager
            from core.llm.content_filter import content_filter
            
            self.logger.info(f"🤖 Generating content for: {task_info.description}")
            response = await llm_manager.generate(task_info.description)
            
            # Create project folder structure
            from modules.tools.file_manager import FileManager
            file_manager = FileManager()
            
            # Determine main filename
            main_filename = self._determine_main_filename(task_info, response.content)
            
            # Filter content to extract only clean code
            file_extension = main_filename.split('.')[-1] if '.' in main_filename else 'generic'
            clean_content = content_filter.extract_code(response.content, file_extension)
            
            # Create full path with project folder
            file_path = f"{task_info.folder_name}/{main_filename}"
            
            # Save filtered content
            save_result = await file_manager.execute(
                'write', 
                file_path, 
                content=clean_content
            )
            
            files_created = [save_result.metadata.get('path')]
            
            # Create additional project structure if needed
            if task_info.task_type == 'website':
                additional_files = await self._create_website_structure(task_info, file_manager)
                files_created.extend(additional_files)
            
            await llm_manager.cleanup()
            
            return {
                'success': True,
                'content_length': len(clean_content),
                'original_length': len(response.content),
                'model': response.model,
                'tokens_used': response.tokens_used,
                'files_created': files_created,
                'main_file': save_result.metadata.get('path'),
                'content_filtered': len(clean_content) < len(response.content)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Task execution failed: {e}")
            try:
                await llm_manager.cleanup()
            except:
                pass
            raise e
    
    def _determine_main_filename(self, task_info, content: str) -> str:
        """Determine the main filename for the generated content"""
        
        # Check if content looks like HTML
        if '<html' in content.lower() or '<!doctype html' in content.lower():
            return 'index.html'
        elif task_info.task_type == 'website':
            return 'index.html'
        elif task_info.task_type == 'script':
            return 'main.py'
        else:
            return task_info.file_suggestions[0] if task_info.file_suggestions else 'main.html'
    
    async def _create_website_structure(self, task_info, file_manager) -> List[str]:
        """Create basic website project structure"""
        
        additional_files = []
        base_path = task_info.folder_name
        
        try:
            # Create basic CSS file
            css_content = """/* Basic styles for """ + task_info.project_name + """ */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Add your custom styles here */
"""
            
            css_result = await file_manager.execute(
                'write',
                f"{base_path}/styles/main.css",
                content=css_content
            )
            additional_files.append(css_result.metadata.get('path'))
            
            # Create basic JS file
            js_content = """// JavaScript for """ + task_info.project_name + """
document.addEventListener('DOMContentLoaded', function() {
    console.log('""" + task_info.project_name + """ loaded successfully');
    
    // Add your JavaScript code here
});
"""
            
            js_result = await file_manager.execute(
                'write',
                f"{base_path}/js/script.js",
                content=js_content
            )
            additional_files.append(js_result.metadata.get('path'))
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not create additional structure: {e}")
        
        return additional_files
        
        # Original workflow execution for non-generation tasks
        for step in workflow.steps:
            try:
                if self.execution_engine:
                    from core.engines.execution.execution_engine import ExecutionRequest
                    request = ExecutionRequest(
                        request_id=f"{workflow.id}_{step.id}",
                        task_description=step.description,
                        tools_required=[step.tool],
                        parameters=step.parameters
                    )
                    
                    result = await self.execution_engine.execute_request(request)
                    results[step.id] = result
                else:
                    # Direct tool execution
                    from modules.tools.base_tool import tool_registry
                    result = await tool_registry.execute_tool(step.tool, **step.parameters)
                    results[step.id] = {
                        "success": result.success,
                        "output": result.output,
                        "error": result.error_message
                    }
                    
            except Exception as e:
                results[step.id] = {
                    "success": False,
                    "error": str(e)
                }
        
        workflow.status = WorkflowStatus.COMPLETED
        return {
            "workflow_id": workflow.id,
            "status": "completed", 
            "results": results,
            "success": all(r.get("success", False) for r in results.values())
        }
        
        # Original workflow execution for non-LLM tasks
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
    
    def _extract_filename(self, description: str) -> str:
        """Extract filename from description with intelligent path handling"""
        import re
        import os
        
        # Enhanced patterns for better path detection
        patterns = [
            # Full paths with directories
            r'save\s+(?:it\s+)?(?:as|to|in)\s+([^\s]+/[^\s/]+\.\w+)',  # save as path/file.ext
            r'save\s+(?:it\s+)?(?:as|to|in)\s+"([^"]+/[^"/]+\.\w+)"',  # save as "path/file.ext"
            r'save\s+(?:it\s+)?(?:as|to|in)\s+\'([^\']+/[^\'/]+\.\w+)\'',  # save as 'path/file.ext'
            
            # Create/write with paths
            r'create\s+([^\s]+/[^\s/]+\.\w+)',  # create path/file.ext
            r'write\s+(?:to\s+)?([^\s]+/[^\s/]+\.\w+)',  # write to path/file.ext
            
            # Simple filenames
            r'save\s+(?:it\s+)?(?:as|to)\s+([^\s]+\.\w+)',  # save as file.ext
            r'create\s+([^\s]+\.\w+)',  # create file.ext
            r'write\s+([^\s]+\.\w+)',  # write file.ext
            
            # Any path/filename pattern
            r'([^\s]+/[^\s/]+\.\w+)',  # any path/file.ext
            r'([^\s]+\.\w+)'  # any file.ext
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description.lower())
            if match:
                filename = match.group(1)
                
                # Clean up the filename
                filename = filename.strip('\'"')
                
                self.logger.info(f"📝 Extracted filename: {filename}")
                return filename
        
        # Generate intelligent default based on content and context
        return self._generate_smart_filename(description)
    
    def _generate_smart_filename(self, description: str) -> str:
        """Generate smart filename based on description context"""
        desc_lower = description.lower()
        
        # Detect file type from description
        if any(word in desc_lower for word in ['python', 'script', '.py']):
            if 'calculator' in desc_lower:
                return 'calculator.py'
            elif 'data' in desc_lower and 'analysis' in desc_lower:
                return 'data_analyzer.py'
            elif 'hello' in desc_lower:
                return 'hello_world.py'
            else:
                return 'script.py'
                
        elif any(word in desc_lower for word in ['html', 'website', 'page', 'web']):
            if 'portfolio' in desc_lower:
                return 'portfolio.html'
            elif 'landing' in desc_lower:
                return 'landing_page.html'
            elif 'contact' in desc_lower:
                return 'contact.html'
            else:
                return 'index.html'
                
        elif any(word in desc_lower for word in ['css', 'style', 'stylesheet']):
            if 'main' in desc_lower:
                return 'styles/main.css'
            elif 'component' in desc_lower:
                return 'styles/components.css'
            else:
                return 'styles/style.css'
                
        elif any(word in desc_lower for word in ['javascript', 'js', 'function']):
            if 'component' in desc_lower:
                return 'js/components.js'
            elif 'util' in desc_lower:
                return 'js/utils.js'
            else:
                return 'js/script.js'
                
        elif any(word in desc_lower for word in ['json', 'config', 'data']):
            return 'data/config.json'
            
        else:
            return 'generated_file.txt'
    
    def list_workflows(self) -> List[SimpleWorkflow]:
        """List all workflows"""
        return list(self.workflows.values())

# Global workflow engine
workflow_engine = SimpleWorkflowEngine()
