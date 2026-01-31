"""
Task Decomposer - Break complex tasks into manageable subtasks
Uses simplified state machine approach (LangGraph alternative)
"""

import json
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class TaskType(Enum):
    RESEARCH = "research"
    DEVELOPMENT = "development"
    ANALYSIS = "analysis"
    CREATION = "creation"
    COMMUNICATION = "communication"
    SYSTEM_OPERATION = "system_operation"

@dataclass
class Subtask:
    id: str
    name: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    estimated_time: int  # minutes
    dependencies: List[str]
    tools_required: List[str]
    success_criteria: str
    confidence: float = 0.8
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TaskDecomposition:
    original_task: str
    subtasks: List[Subtask]
    execution_order: List[str]  # subtask IDs in order
    total_estimated_time: int
    confidence: float
    reasoning: str

class TaskDecomposer:
    """Decompose complex tasks into executable subtasks"""
    
    def __init__(self):
        self.logger = logging.getLogger("task_decomposer")
        
        # Task patterns for common operations
        self.task_patterns = {
            "build_application": {
                "subtasks": [
                    "analyze_requirements",
                    "design_architecture", 
                    "setup_environment",
                    "implement_core_features",
                    "add_user_interface",
                    "implement_testing",
                    "deploy_application"
                ],
                "complexity": TaskComplexity.VERY_COMPLEX
            },
            "research_topic": {
                "subtasks": [
                    "define_research_scope",
                    "gather_information",
                    "analyze_findings",
                    "synthesize_results",
                    "create_summary"
                ],
                "complexity": TaskComplexity.MODERATE
            },
            "write_document": {
                "subtasks": [
                    "outline_structure",
                    "research_content",
                    "write_draft",
                    "review_and_edit",
                    "finalize_document"
                ],
                "complexity": TaskComplexity.MODERATE
            }
        }
    
    def analyze_task_complexity(self, task: str) -> TaskComplexity:
        """Analyze task complexity based on keywords and patterns"""
        task_lower = task.lower()
        
        # Very complex indicators
        very_complex_keywords = [
            "build", "create application", "full stack", "system", "architecture",
            "production", "deploy", "integrate multiple", "end-to-end"
        ]
        
        # Complex indicators
        complex_keywords = [
            "develop", "implement", "design", "analyze complex", "research comprehensive",
            "multiple components", "workflow", "automation"
        ]
        
        # Moderate indicators
        moderate_keywords = [
            "write", "document", "research", "analyze", "plan", "organize",
            "review", "compare", "evaluate"
        ]
        
        # Simple indicators
        simple_keywords = [
            "read", "find", "list", "check", "verify", "copy", "move",
            "delete", "rename", "calculate"
        ]
        
        if any(keyword in task_lower for keyword in very_complex_keywords):
            return TaskComplexity.VERY_COMPLEX
        elif any(keyword in task_lower for keyword in complex_keywords):
            return TaskComplexity.COMPLEX
        elif any(keyword in task_lower for keyword in moderate_keywords):
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def identify_task_type(self, task: str) -> TaskType:
        """Identify the primary type of task"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["research", "investigate", "study", "explore"]):
            return TaskType.RESEARCH
        elif any(word in task_lower for word in ["build", "develop", "code", "implement", "program"]):
            return TaskType.DEVELOPMENT
        elif any(word in task_lower for word in ["analyze", "evaluate", "assess", "review"]):
            return TaskType.ANALYSIS
        elif any(word in task_lower for word in ["create", "write", "design", "make"]):
            return TaskType.CREATION
        elif any(word in task_lower for word in ["email", "message", "communicate", "notify"]):
            return TaskType.COMMUNICATION
        else:
            return TaskType.SYSTEM_OPERATION
    
    def estimate_time(self, complexity: TaskComplexity, task_type: TaskType) -> int:
        """Estimate time in minutes based on complexity and type"""
        base_times = {
            TaskComplexity.SIMPLE: 15,
            TaskComplexity.MODERATE: 60,
            TaskComplexity.COMPLEX: 180,
            TaskComplexity.VERY_COMPLEX: 480
        }
        
        type_multipliers = {
            TaskType.RESEARCH: 1.2,
            TaskType.DEVELOPMENT: 1.5,
            TaskType.ANALYSIS: 1.0,
            TaskType.CREATION: 1.3,
            TaskType.COMMUNICATION: 0.8,
            TaskType.SYSTEM_OPERATION: 0.7
        }
        
        base_time = base_times[complexity]
        multiplier = type_multipliers[task_type]
        
        return int(base_time * multiplier)
    
    def determine_required_tools(self, task_type: TaskType, description: str) -> List[str]:
        """Determine which tools are needed for a subtask"""
        tools = []
        desc_lower = description.lower()
        
        # Always available tools
        if any(word in desc_lower for word in ["file", "read", "write", "create", "save"]):
            tools.append("file_manager")
        
        if any(word in desc_lower for word in ["command", "execute", "run", "install"]):
            tools.append("terminal_executor")
        
        if any(word in desc_lower for word in ["search", "research", "find information"]):
            tools.append("web_search")
        
        if any(word in desc_lower for word in ["calculate", "compute", "math"]):
            tools.append("calculator")
        
        if any(word in desc_lower for word in ["ask", "confirm", "approval", "input"]):
            tools.append("human_input")
        
        return tools
    
    async def decompose_task(self, task: str) -> TaskDecomposition:
        """Decompose a task into subtasks"""
        
        self.logger.info(f"Decomposing task: {task}")
        
        # Analyze task
        complexity = self.analyze_task_complexity(task)
        task_type = self.identify_task_type(task)
        
        # Check for known patterns
        subtasks = []
        
        if complexity == TaskComplexity.SIMPLE:
            # Simple tasks don't need decomposition
            subtask = Subtask(
                id="main_task",
                name=task,
                description=task,
                task_type=task_type,
                complexity=complexity,
                estimated_time=self.estimate_time(complexity, task_type),
                dependencies=[],
                tools_required=self.determine_required_tools(task_type, task),
                success_criteria=f"Successfully completed: {task}"
            )
            subtasks = [subtask]
            execution_order = ["main_task"]
            
        else:
            # Complex tasks need decomposition
            subtasks = await self._decompose_complex_task(task, complexity, task_type)
            execution_order = self._determine_execution_order(subtasks)
        
        total_time = sum(st.estimated_time for st in subtasks)
        avg_confidence = sum(st.confidence for st in subtasks) / len(subtasks)
        
        decomposition = TaskDecomposition(
            original_task=task,
            subtasks=subtasks,
            execution_order=execution_order,
            total_estimated_time=total_time,
            confidence=avg_confidence,
            reasoning=f"Decomposed {complexity.value} {task_type.value} task into {len(subtasks)} subtasks"
        )
        
        self.logger.info(f"Task decomposed into {len(subtasks)} subtasks, estimated {total_time} minutes")
        return decomposition
    
    async def _decompose_complex_task(self, task: str, complexity: TaskComplexity, task_type: TaskType) -> List[Subtask]:
        """Decompose complex tasks using patterns and heuristics"""
        
        subtasks = []
        task_lower = task.lower()
        
        # Development tasks
        if task_type == TaskType.DEVELOPMENT:
            if "application" in task_lower or "app" in task_lower:
                subtasks = [
                    Subtask("req_analysis", "Analyze Requirements", 
                           "Understand what needs to be built", TaskType.ANALYSIS, 
                           TaskComplexity.MODERATE, 60, [], ["file_manager"], 
                           "Requirements clearly documented"),
                    Subtask("arch_design", "Design Architecture", 
                           "Plan the system architecture", TaskType.CREATION, 
                           TaskComplexity.COMPLEX, 120, ["req_analysis"], ["file_manager"], 
                           "Architecture diagram and plan created"),
                    Subtask("setup_env", "Setup Environment", 
                           "Prepare development environment", TaskType.SYSTEM_OPERATION, 
                           TaskComplexity.MODERATE, 45, ["arch_design"], ["terminal_executor"], 
                           "Development environment ready"),
                    Subtask("core_impl", "Implement Core Features", 
                           "Build main functionality", TaskType.DEVELOPMENT, 
                           TaskComplexity.VERY_COMPLEX, 300, ["setup_env"], ["file_manager", "terminal_executor"], 
                           "Core features working"),
                    Subtask("testing", "Add Testing", 
                           "Create and run tests", TaskType.DEVELOPMENT, 
                           TaskComplexity.COMPLEX, 120, ["core_impl"], ["file_manager", "terminal_executor"], 
                           "Tests passing"),
                    Subtask("deployment", "Deploy Application", 
                           "Deploy to production", TaskType.SYSTEM_OPERATION, 
                           TaskComplexity.COMPLEX, 90, ["testing"], ["terminal_executor"], 
                           "Application deployed and accessible")
                ]
        
        # Research tasks
        elif task_type == TaskType.RESEARCH:
            subtasks = [
                Subtask("define_scope", "Define Research Scope", 
                       "Clarify what to research", TaskType.ANALYSIS, 
                       TaskComplexity.SIMPLE, 30, [], ["file_manager"], 
                       "Research scope defined"),
                Subtask("gather_info", "Gather Information", 
                       "Search for relevant information", TaskType.RESEARCH, 
                       TaskComplexity.MODERATE, 90, ["define_scope"], ["web_search", "file_manager"], 
                       "Relevant information collected"),
                Subtask("analyze_findings", "Analyze Findings", 
                       "Process and analyze collected data", TaskType.ANALYSIS, 
                       TaskComplexity.MODERATE, 75, ["gather_info"], ["file_manager"], 
                       "Analysis completed"),
                Subtask("create_summary", "Create Summary", 
                       "Synthesize findings into summary", TaskType.CREATION, 
                       TaskComplexity.MODERATE, 60, ["analyze_findings"], ["file_manager"], 
                       "Summary document created")
            ]
        
        # Creation tasks
        elif task_type == TaskType.CREATION:
            subtasks = [
                Subtask("plan_structure", "Plan Structure", 
                       "Outline the structure", TaskType.ANALYSIS, 
                       TaskComplexity.SIMPLE, 30, [], ["file_manager"], 
                       "Structure planned"),
                Subtask("create_content", "Create Content", 
                       "Generate the main content", TaskType.CREATION, 
                       TaskComplexity.COMPLEX, 150, ["plan_structure"], ["file_manager", "web_search"], 
                       "Content created"),
                Subtask("review_refine", "Review and Refine", 
                       "Review and improve the content", TaskType.ANALYSIS, 
                       TaskComplexity.MODERATE, 60, ["create_content"], ["file_manager"], 
                       "Content reviewed and refined")
            ]
        
        # Default decomposition for other tasks
        else:
            subtasks = [
                Subtask("prepare", "Prepare", 
                       "Prepare for the task", TaskType.SYSTEM_OPERATION, 
                       TaskComplexity.SIMPLE, 15, [], ["file_manager"], 
                       "Preparation complete"),
                Subtask("execute", "Execute Main Task", 
                       f"Execute: {task}", task_type, 
                       complexity, self.estimate_time(complexity, task_type), ["prepare"], 
                       self.determine_required_tools(task_type, task), 
                       f"Task completed: {task}"),
                Subtask("verify", "Verify Results", 
                       "Verify task completion", TaskType.ANALYSIS, 
                       TaskComplexity.SIMPLE, 15, ["execute"], ["file_manager"], 
                       "Results verified")
            ]
        
        return subtasks
    
    def _determine_execution_order(self, subtasks: List[Subtask]) -> List[str]:
        """Determine optimal execution order based on dependencies"""
        
        # Simple topological sort
        order = []
        remaining = {st.id: st for st in subtasks}
        
        while remaining:
            # Find tasks with no unmet dependencies
            ready = []
            for task_id, subtask in remaining.items():
                if all(dep in order for dep in subtask.dependencies):
                    ready.append(task_id)
            
            if not ready:
                # Circular dependency or error - just add remaining in order
                ready = list(remaining.keys())
            
            # Add first ready task
            next_task = ready[0]
            order.append(next_task)
            del remaining[next_task]
        
        return order
    
    def validate_decomposition(self, decomposition: TaskDecomposition) -> bool:
        """Validate that decomposition is logical and executable"""
        
        # Check that all dependencies exist
        subtask_ids = {st.id for st in decomposition.subtasks}
        for subtask in decomposition.subtasks:
            for dep in subtask.dependencies:
                if dep not in subtask_ids:
                    self.logger.error(f"Invalid dependency {dep} in subtask {subtask.id}")
                    return False
        
        # Check execution order covers all subtasks
        if set(decomposition.execution_order) != subtask_ids:
            self.logger.error("Execution order doesn't match subtasks")
            return False
        
        return True
