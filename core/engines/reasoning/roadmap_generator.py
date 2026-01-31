"""
Roadmap Generator - Create execution plans with dependencies
"""

import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

from .task_decomposer import TaskDecomposition, Subtask

@dataclass
class ExecutionStep:
    step_id: str
    subtask_id: str
    name: str
    description: str
    estimated_duration: int  # minutes
    tools_required: List[str]
    dependencies: List[str]  # step IDs this depends on
    success_criteria: str
    parallel_group: Optional[str] = None  # Steps that can run in parallel
    
@dataclass
class Roadmap:
    roadmap_id: str
    original_task: str
    steps: List[ExecutionStep]
    execution_phases: List[List[str]]  # Groups of step IDs that can run in parallel
    total_estimated_time: int  # minutes
    critical_path: List[str]  # step IDs on critical path
    confidence: float
    created_at: datetime
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        return result

class RoadmapGenerator:
    """Generate executable roadmaps from task decompositions"""
    
    def __init__(self):
        self.logger = logging.getLogger("roadmap_generator")
        
    async def generate_roadmap(self, decomposition: TaskDecomposition) -> Roadmap:
        """Generate an executable roadmap from task decomposition"""
        
        self.logger.info(f"Generating roadmap for: {decomposition.original_task}")
        
        # Convert subtasks to execution steps
        steps = self._create_execution_steps(decomposition.subtasks)
        
        # Determine execution phases (parallel groups)
        phases = self._determine_execution_phases(steps)
        
        # Find critical path
        critical_path = self._find_critical_path(steps)
        
        # Calculate total time considering parallelization
        total_time = self._calculate_total_time(steps, phases)
        
        roadmap = Roadmap(
            roadmap_id=f"roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            original_task=decomposition.original_task,
            steps=steps,
            execution_phases=phases,
            total_estimated_time=total_time,
            critical_path=critical_path,
            confidence=decomposition.confidence,
            created_at=datetime.now()
        )
        
        self.logger.info(f"Generated roadmap with {len(steps)} steps in {len(phases)} phases")
        return roadmap
    
    def _create_execution_steps(self, subtasks: List[Subtask]) -> List[ExecutionStep]:
        """Convert subtasks to execution steps"""
        steps = []
        
        for i, subtask in enumerate(subtasks):
            step = ExecutionStep(
                step_id=f"step_{i+1:02d}",
                subtask_id=subtask.id,
                name=subtask.name,
                description=subtask.description,
                estimated_duration=subtask.estimated_time,
                tools_required=subtask.tools_required,
                dependencies=subtask.dependencies,
                success_criteria=subtask.success_criteria
            )
            steps.append(step)
        
        return steps
    
    def _determine_execution_phases(self, steps: List[ExecutionStep]) -> List[List[str]]:
        """Group steps into phases that can execute in parallel"""
        
        phases = []
        remaining_steps = {step.step_id: step for step in steps}
        completed_steps = set()
        
        while remaining_steps:
            # Find steps that can run now (dependencies satisfied)
            ready_steps = []
            
            for step_id, step in remaining_steps.items():
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self._find_step_by_subtask_id(dep, steps).step_id in completed_steps
                    for dep in step.dependencies
                )
                
                if deps_satisfied:
                    ready_steps.append(step_id)
            
            if not ready_steps:
                # Should not happen with valid dependencies
                self.logger.warning("No ready steps found, adding remaining steps")
                ready_steps = list(remaining_steps.keys())
            
            # Group parallel steps
            parallel_groups = self._group_parallel_steps(
                [remaining_steps[sid] for sid in ready_steps]
            )
            
            # Add each parallel group as a phase
            for group in parallel_groups:
                phase_step_ids = [step.step_id for step in group]
                phases.append(phase_step_ids)
                
                # Mark as completed and remove from remaining
                for step in group:
                    completed_steps.add(step.step_id)
                    del remaining_steps[step.step_id]
        
        return phases
    
    def _group_parallel_steps(self, ready_steps: List[ExecutionStep]) -> List[List[ExecutionStep]]:
        """Group steps that can run in parallel"""
        
        # For now, simple heuristic: steps with different tool requirements can run in parallel
        # In production, this would be more sophisticated
        
        groups = []
        remaining = ready_steps.copy()
        
        while remaining:
            # Start new group with first remaining step
            current_group = [remaining.pop(0)]
            current_tools = set(current_group[0].tools_required)
            
            # Add compatible steps to current group
            compatible = []
            for step in remaining:
                step_tools = set(step.tools_required)
                # Can run in parallel if no tool conflicts
                if not (current_tools & step_tools):
                    compatible.append(step)
                    current_tools.update(step_tools)
            
            # Add compatible steps to group and remove from remaining
            for step in compatible:
                current_group.append(step)
                remaining.remove(step)
            
            groups.append(current_group)
        
        return groups
    
    def _find_step_by_subtask_id(self, subtask_id: str, steps: List[ExecutionStep]) -> Optional[ExecutionStep]:
        """Find step by subtask ID"""
        for step in steps:
            if step.subtask_id == subtask_id:
                return step
        return None
    
    def _find_critical_path(self, steps: List[ExecutionStep]) -> List[str]:
        """Find the critical path (longest dependency chain)"""
        
        # Build dependency graph
        step_map = {step.step_id: step for step in steps}
        
        # Calculate longest path to each step
        longest_paths = {}
        
        def calculate_longest_path(step_id: str) -> int:
            if step_id in longest_paths:
                return longest_paths[step_id]
            
            step = step_map[step_id]
            
            if not step.dependencies:
                longest_paths[step_id] = step.estimated_duration
                return step.estimated_duration
            
            # Find longest path through dependencies
            max_dep_path = 0
            for dep_subtask_id in step.dependencies:
                dep_step = self._find_step_by_subtask_id(dep_subtask_id, steps)
                if dep_step:
                    dep_path = calculate_longest_path(dep_step.step_id)
                    max_dep_path = max(max_dep_path, dep_path)
            
            longest_paths[step_id] = max_dep_path + step.estimated_duration
            return longest_paths[step_id]
        
        # Calculate for all steps
        for step in steps:
            calculate_longest_path(step.step_id)
        
        # Find the step with longest path (end of critical path)
        critical_end = max(longest_paths.keys(), key=lambda x: longest_paths[x])
        
        # Trace back the critical path
        critical_path = []
        current = critical_end
        
        while current:
            critical_path.append(current)
            step = step_map[current]
            
            # Find the dependency that leads to longest path
            next_step = None
            max_path = 0
            
            for dep_subtask_id in step.dependencies:
                dep_step = self._find_step_by_subtask_id(dep_subtask_id, steps)
                if dep_step and longest_paths[dep_step.step_id] > max_path:
                    max_path = longest_paths[dep_step.step_id]
                    next_step = dep_step.step_id
            
            current = next_step
        
        critical_path.reverse()
        return critical_path
    
    def _calculate_total_time(self, steps: List[ExecutionStep], phases: List[List[str]]) -> int:
        """Calculate total execution time considering parallelization"""
        
        step_map = {step.step_id: step for step in steps}
        total_time = 0
        
        for phase in phases:
            # Time for this phase is the maximum time of parallel steps
            phase_time = max(
                step_map[step_id].estimated_duration 
                for step_id in phase
            )
            total_time += phase_time
        
        return total_time
    
    def optimize_roadmap(self, roadmap: Roadmap) -> Roadmap:
        """Optimize roadmap for better execution"""
        
        # For now, basic optimization
        # In production, this would include:
        # - Resource optimization
        # - Risk mitigation
        # - Alternative path planning
        
        self.logger.info(f"Optimizing roadmap {roadmap.roadmap_id}")
        
        # Simple optimization: ensure critical path steps are prioritized
        optimized_steps = roadmap.steps.copy()
        
        # Mark critical path steps
        for step in optimized_steps:
            if step.step_id in roadmap.critical_path:
                step.parallel_group = "critical"
        
        # Recalculate phases with optimization
        optimized_phases = self._determine_execution_phases(optimized_steps)
        
        return Roadmap(
            roadmap_id=roadmap.roadmap_id + "_optimized",
            original_task=roadmap.original_task,
            steps=optimized_steps,
            execution_phases=optimized_phases,
            total_estimated_time=self._calculate_total_time(optimized_steps, optimized_phases),
            critical_path=roadmap.critical_path,
            confidence=roadmap.confidence * 0.95,  # Slight confidence reduction for optimization
            created_at=datetime.now()
        )
    
    def validate_roadmap(self, roadmap: Roadmap) -> Tuple[bool, List[str]]:
        """Validate roadmap for executability"""
        
        errors = []
        
        # Check all steps have valid tools
        for step in roadmap.steps:
            if not step.tools_required:
                errors.append(f"Step {step.step_id} has no tools specified")
        
        # Check dependencies are valid
        step_subtask_ids = {step.subtask_id for step in roadmap.steps}
        for step in roadmap.steps:
            for dep in step.dependencies:
                if dep not in step_subtask_ids:
                    errors.append(f"Step {step.step_id} has invalid dependency: {dep}")
        
        # Check phases cover all steps
        all_phase_steps = set()
        for phase in roadmap.execution_phases:
            all_phase_steps.update(phase)
        
        all_step_ids = {step.step_id for step in roadmap.steps}
        if all_phase_steps != all_step_ids:
            errors.append("Execution phases don't cover all steps")
        
        return len(errors) == 0, errors
