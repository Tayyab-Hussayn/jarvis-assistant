"""
Anti-Hallucination System - Validation loops and logic checking
Prevents the AI from going off-track or making logical errors
"""

import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .task_decomposer import TaskDecomposition
from .roadmap_generator import Roadmap

class ValidationLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ValidationResult(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class ValidationCheck:
    check_id: str
    name: str
    description: str
    level: ValidationLevel
    result: ValidationResult
    confidence: float
    details: str
    suggestions: List[str]

class AntiHallucinationSystem:
    """Prevent logical errors and hallucinations in reasoning"""
    
    def __init__(self):
        self.logger = logging.getLogger("anti_hallucination")
        
        # Validation rules
        self.validation_rules = {
            "task_coherence": self._check_task_coherence,
            "dependency_logic": self._check_dependency_logic,
            "resource_availability": self._check_resource_availability,
            "time_estimates": self._check_time_estimates,
            "tool_compatibility": self._check_tool_compatibility,
            "success_criteria": self._check_success_criteria,
            "logical_sequence": self._check_logical_sequence
        }
    
    async def validate_decomposition(self, decomposition: TaskDecomposition) -> List[ValidationCheck]:
        """Validate task decomposition for logical consistency"""
        
        self.logger.info(f"Validating decomposition for: {decomposition.original_task}")
        
        checks = []
        
        # Run all validation rules
        for rule_name, rule_func in self.validation_rules.items():
            try:
                check = await rule_func(decomposition)
                checks.append(check)
            except Exception as e:
                self.logger.error(f"Validation rule {rule_name} failed: {e}")
                checks.append(ValidationCheck(
                    check_id=rule_name,
                    name=rule_name.replace("_", " ").title(),
                    description=f"Validation rule {rule_name}",
                    level=ValidationLevel.MEDIUM,
                    result=ValidationResult.FAIL,
                    confidence=0.0,
                    details=f"Rule execution failed: {e}",
                    suggestions=["Review validation rule implementation"]
                ))
        
        # Overall assessment
        failed_checks = [c for c in checks if c.result == ValidationResult.FAIL]
        warning_checks = [c for c in checks if c.result == ValidationResult.WARNING]
        
        self.logger.info(f"Validation complete: {len(failed_checks)} failures, {len(warning_checks)} warnings")
        
        return checks
    
    async def validate_roadmap(self, roadmap: Roadmap) -> List[ValidationCheck]:
        """Validate roadmap for executability"""
        
        self.logger.info(f"Validating roadmap: {roadmap.roadmap_id}")
        
        checks = []
        
        # Roadmap-specific validations
        checks.append(await self._check_roadmap_completeness(roadmap))
        checks.append(await self._check_execution_phases(roadmap))
        checks.append(await self._check_critical_path(roadmap))
        checks.append(await self._check_parallel_execution(roadmap))
        
        return checks
    
    async def _check_task_coherence(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if subtasks are coherent with original task"""
        
        original = decomposition.original_task.lower()
        subtask_names = [st.name.lower() for st in decomposition.subtasks]
        
        # Simple keyword matching for coherence
        original_keywords = set(original.split())
        subtask_keywords = set()
        for name in subtask_names:
            subtask_keywords.update(name.split())
        
        # Check overlap
        overlap = len(original_keywords & subtask_keywords)
        total_original = len(original_keywords)
        
        coherence_score = overlap / total_original if total_original > 0 else 0.5
        
        if coherence_score > 0.3:
            result = ValidationResult.PASS
            details = f"Good coherence: {coherence_score:.2f} keyword overlap"
            suggestions = []
        elif coherence_score > 0.1:
            result = ValidationResult.WARNING
            details = f"Moderate coherence: {coherence_score:.2f} keyword overlap"
            suggestions = ["Review subtask relevance to original task"]
        else:
            result = ValidationResult.FAIL
            details = f"Poor coherence: {coherence_score:.2f} keyword overlap"
            suggestions = ["Subtasks may not be relevant to original task", "Reconsider decomposition approach"]
        
        return ValidationCheck(
            check_id="task_coherence",
            name="Task Coherence",
            description="Check if subtasks align with original task",
            level=ValidationLevel.HIGH,
            result=result,
            confidence=0.8,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_dependency_logic(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if dependencies make logical sense"""
        
        subtask_map = {st.id: st for st in decomposition.subtasks}
        issues = []
        
        # Check for circular dependencies
        def has_circular_dependency(task_id: str, visited: set, path: set) -> bool:
            if task_id in path:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            path.add(task_id)
            
            task = subtask_map.get(task_id)
            if task:
                for dep in task.dependencies:
                    if has_circular_dependency(dep, visited, path):
                        return True
            
            path.remove(task_id)
            return False
        
        # Check each subtask
        for subtask in decomposition.subtasks:
            # Check for circular dependencies
            if has_circular_dependency(subtask.id, set(), set()):
                issues.append(f"Circular dependency detected involving {subtask.id}")
            
            # Check if dependencies exist
            for dep in subtask.dependencies:
                if dep not in subtask_map:
                    issues.append(f"Invalid dependency {dep} in {subtask.id}")
        
        if not issues:
            result = ValidationResult.PASS
            details = "All dependencies are valid"
            suggestions = []
        else:
            result = ValidationResult.FAIL
            details = f"Dependency issues found: {'; '.join(issues)}"
            suggestions = ["Fix circular dependencies", "Ensure all dependencies exist"]
        
        return ValidationCheck(
            check_id="dependency_logic",
            name="Dependency Logic",
            description="Check dependency relationships",
            level=ValidationLevel.CRITICAL,
            result=result,
            confidence=0.9,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_resource_availability(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if required tools/resources are available"""
        
        # Available tools (from our tool registry)
        available_tools = {
            "file_manager", "terminal_executor", "web_search", 
            "calculator", "human_input"
        }
        
        missing_tools = set()
        for subtask in decomposition.subtasks:
            for tool in subtask.tools_required:
                if tool not in available_tools:
                    missing_tools.add(tool)
        
        if not missing_tools:
            result = ValidationResult.PASS
            details = "All required tools are available"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Missing tools: {', '.join(missing_tools)}"
            suggestions = [f"Implement or acquire missing tools: {', '.join(missing_tools)}"]
        
        return ValidationCheck(
            check_id="resource_availability",
            name="Resource Availability",
            description="Check if required resources are available",
            level=ValidationLevel.HIGH,
            result=result,
            confidence=0.95,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_time_estimates(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if time estimates are reasonable"""
        
        total_time = decomposition.total_estimated_time
        num_subtasks = len(decomposition.subtasks)
        avg_time = total_time / num_subtasks if num_subtasks > 0 else 0
        
        issues = []
        
        # Check for unrealistic estimates
        for subtask in decomposition.subtasks:
            if subtask.estimated_time < 5:
                issues.append(f"{subtask.name}: too short ({subtask.estimated_time}min)")
            elif subtask.estimated_time > 480:  # 8 hours
                issues.append(f"{subtask.name}: too long ({subtask.estimated_time}min)")
        
        # Check total time reasonableness
        if total_time > 2880:  # 48 hours
            issues.append(f"Total time very long: {total_time}min")
        
        if not issues:
            result = ValidationResult.PASS
            details = f"Time estimates reasonable (total: {total_time}min, avg: {avg_time:.1f}min)"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Time estimate issues: {'; '.join(issues)}"
            suggestions = ["Review and adjust time estimates", "Consider breaking down long tasks"]
        
        return ValidationCheck(
            check_id="time_estimates",
            name="Time Estimates",
            description="Check reasonableness of time estimates",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.7,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_tool_compatibility(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if tool combinations make sense"""
        
        # Tool compatibility rules
        incompatible_combinations = [
            # Add specific incompatible tool combinations here
        ]
        
        issues = []
        for subtask in decomposition.subtasks:
            tools = set(subtask.tools_required)
            
            # Check for incompatible combinations
            for incompatible in incompatible_combinations:
                if set(incompatible).issubset(tools):
                    issues.append(f"{subtask.name}: incompatible tools {incompatible}")
        
        if not issues:
            result = ValidationResult.PASS
            details = "No tool compatibility issues"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Tool compatibility issues: {'; '.join(issues)}"
            suggestions = ["Review tool combinations", "Consider alternative approaches"]
        
        return ValidationCheck(
            check_id="tool_compatibility",
            name="Tool Compatibility",
            description="Check tool compatibility",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.8,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_success_criteria(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if success criteria are well-defined"""
        
        issues = []
        for subtask in decomposition.subtasks:
            criteria = subtask.success_criteria.lower()
            
            # Check for vague criteria
            vague_words = ["good", "nice", "proper", "appropriate", "suitable"]
            if any(word in criteria for word in vague_words):
                issues.append(f"{subtask.name}: vague success criteria")
            
            # Check for measurable criteria
            if len(criteria) < 10:
                issues.append(f"{subtask.name}: success criteria too brief")
        
        if not issues:
            result = ValidationResult.PASS
            details = "Success criteria are well-defined"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Success criteria issues: {'; '.join(issues)}"
            suggestions = ["Make success criteria more specific and measurable"]
        
        return ValidationCheck(
            check_id="success_criteria",
            name="Success Criteria",
            description="Check quality of success criteria",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.7,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_logical_sequence(self, decomposition: TaskDecomposition) -> ValidationCheck:
        """Check if execution order makes logical sense"""
        
        # This is a simplified check - in production would be more sophisticated
        sequence_issues = []
        
        # Check if preparation tasks come before execution
        prep_tasks = [st for st in decomposition.subtasks if "prepare" in st.name.lower() or "setup" in st.name.lower()]
        exec_tasks = [st for st in decomposition.subtasks if "implement" in st.name.lower() or "execute" in st.name.lower()]
        
        for prep_task in prep_tasks:
            prep_index = decomposition.execution_order.index(prep_task.id)
            for exec_task in exec_tasks:
                if exec_task.id in decomposition.execution_order:
                    exec_index = decomposition.execution_order.index(exec_task.id)
                    if prep_index > exec_index:
                        sequence_issues.append(f"Preparation task {prep_task.name} comes after execution task {exec_task.name}")
        
        if not sequence_issues:
            result = ValidationResult.PASS
            details = "Logical sequence appears correct"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Sequence issues: {'; '.join(sequence_issues)}"
            suggestions = ["Review task ordering", "Ensure preparation comes before execution"]
        
        return ValidationCheck(
            check_id="logical_sequence",
            name="Logical Sequence",
            description="Check logical ordering of tasks",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.6,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_roadmap_completeness(self, roadmap: Roadmap) -> ValidationCheck:
        """Check if roadmap covers all necessary aspects"""
        
        issues = []
        
        # Check if roadmap has steps
        if not roadmap.steps:
            issues.append("Roadmap has no steps")
        
        # Check if execution phases exist
        if not roadmap.execution_phases:
            issues.append("No execution phases defined")
        
        # Check if critical path exists
        if not roadmap.critical_path:
            issues.append("No critical path identified")
        
        if not issues:
            result = ValidationResult.PASS
            details = "Roadmap is complete"
            suggestions = []
        else:
            result = ValidationResult.FAIL
            details = f"Completeness issues: {'; '.join(issues)}"
            suggestions = ["Ensure roadmap has all required components"]
        
        return ValidationCheck(
            check_id="roadmap_completeness",
            name="Roadmap Completeness",
            description="Check roadmap completeness",
            level=ValidationLevel.CRITICAL,
            result=result,
            confidence=0.9,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_execution_phases(self, roadmap: Roadmap) -> ValidationCheck:
        """Check execution phase logic"""
        
        # Check that all steps are in phases
        all_phase_steps = set()
        for phase in roadmap.execution_phases:
            all_phase_steps.update(phase)
        
        all_step_ids = {step.step_id for step in roadmap.steps}
        
        if all_phase_steps == all_step_ids:
            result = ValidationResult.PASS
            details = "All steps are properly phased"
            suggestions = []
        else:
            missing = all_step_ids - all_phase_steps
            extra = all_phase_steps - all_step_ids
            result = ValidationResult.FAIL
            details = f"Phase mismatch - missing: {missing}, extra: {extra}"
            suggestions = ["Fix execution phase coverage"]
        
        return ValidationCheck(
            check_id="execution_phases",
            name="Execution Phases",
            description="Check execution phase logic",
            level=ValidationLevel.HIGH,
            result=result,
            confidence=0.9,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_critical_path(self, roadmap: Roadmap) -> ValidationCheck:
        """Check critical path validity"""
        
        if not roadmap.critical_path:
            result = ValidationResult.WARNING
            details = "No critical path identified"
            suggestions = ["Identify critical path for better planning"]
        else:
            # Check if critical path steps exist
            step_ids = {step.step_id for step in roadmap.steps}
            invalid_steps = [sid for sid in roadmap.critical_path if sid not in step_ids]
            
            if invalid_steps:
                result = ValidationResult.FAIL
                details = f"Critical path contains invalid steps: {invalid_steps}"
                suggestions = ["Fix critical path step references"]
            else:
                result = ValidationResult.PASS
                details = f"Critical path valid with {len(roadmap.critical_path)} steps"
                suggestions = []
        
        return ValidationCheck(
            check_id="critical_path",
            name="Critical Path",
            description="Check critical path validity",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.8,
            details=details,
            suggestions=suggestions
        )
    
    async def _check_parallel_execution(self, roadmap: Roadmap) -> ValidationCheck:
        """Check parallel execution feasibility"""
        
        issues = []
        
        for phase in roadmap.execution_phases:
            if len(phase) > 1:  # Parallel execution
                phase_steps = [step for step in roadmap.steps if step.step_id in phase]
                
                # Check for tool conflicts
                all_tools = set()
                for step in phase_steps:
                    step_tools = set(step.tools_required)
                    conflicts = all_tools & step_tools
                    if conflicts:
                        issues.append(f"Tool conflicts in parallel phase: {conflicts}")
                    all_tools.update(step_tools)
        
        if not issues:
            result = ValidationResult.PASS
            details = "Parallel execution is feasible"
            suggestions = []
        else:
            result = ValidationResult.WARNING
            details = f"Parallel execution issues: {'; '.join(issues)}"
            suggestions = ["Resolve tool conflicts", "Consider sequential execution for conflicting steps"]
        
        return ValidationCheck(
            check_id="parallel_execution",
            name="Parallel Execution",
            description="Check parallel execution feasibility",
            level=ValidationLevel.MEDIUM,
            result=result,
            confidence=0.7,
            details=details,
            suggestions=suggestions
        )
