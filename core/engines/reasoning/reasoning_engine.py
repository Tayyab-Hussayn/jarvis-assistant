"""
Reasoning Engine Integration - Main coordinator for strategic planning
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .task_decomposer import TaskDecomposer, TaskDecomposition
from .roadmap_generator import RoadmapGenerator, Roadmap
from .anti_hallucination import AntiHallucinationSystem, ValidationCheck
from .track_keeper import TrackKeeper, TrackStatus
from core.llm.llm_manager import llm_manager, LLMResponse

@dataclass
class ReasoningResult:
    success: bool
    decomposition: Optional[TaskDecomposition]
    roadmap: Optional[Roadmap]
    validation_checks: List[ValidationCheck]
    tracking_id: Optional[str]
    confidence: float
    reasoning_time: float
    error_message: str = ""

class ReasoningEngine:
    """Main reasoning engine that coordinates all strategic planning"""
    
    def __init__(self):
        self.logger = logging.getLogger("reasoning_engine")
        
        # Initialize components
        self.task_decomposer = TaskDecomposer()
        self.roadmap_generator = RoadmapGenerator()
        self.anti_hallucination = AntiHallucinationSystem()
        self.track_keeper = TrackKeeper()
        
        # State
        self.active_reasonings: Dict[str, ReasoningResult] = {}
        
        # LLM integration
        self.llm_manager = llm_manager
        
    async def reason_about_task(self, task: str, validation_level: str = "high") -> ReasoningResult:
        """Main reasoning function - analyze task and create execution plan"""
        
        start_time = asyncio.get_event_loop().time()
        self.logger.info(f"Starting reasoning about task: {task}")
        
        try:
            # Step 1: Decompose task
            self.logger.info("Step 1: Decomposing task")
            decomposition = await self.task_decomposer.decompose_task(task)
            
            # Step 2: Validate decomposition
            self.logger.info("Step 2: Validating decomposition")
            validation_checks = await self.anti_hallucination.validate_decomposition(decomposition)
            
            # Check if validation passed
            failed_checks = [c for c in validation_checks if c.result.value == "fail"]
            if failed_checks and validation_level == "high":
                return ReasoningResult(
                    success=False,
                    decomposition=decomposition,
                    roadmap=None,
                    validation_checks=validation_checks,
                    tracking_id=None,
                    confidence=0.0,
                    reasoning_time=asyncio.get_event_loop().time() - start_time,
                    error_message=f"Validation failed: {len(failed_checks)} critical issues"
                )
            
            # Step 3: Generate roadmap
            self.logger.info("Step 3: Generating roadmap")
            roadmap = await self.roadmap_generator.generate_roadmap(decomposition)
            
            # Step 4: Validate roadmap
            self.logger.info("Step 4: Validating roadmap")
            roadmap_checks = await self.anti_hallucination.validate_roadmap(roadmap)
            validation_checks.extend(roadmap_checks)
            
            # Step 5: Start tracking
            self.logger.info("Step 5: Starting progress tracking")
            tracking_id = self.track_keeper.start_tracking(roadmap)
            
            # Calculate overall confidence
            avg_confidence = sum(c.confidence for c in validation_checks) / len(validation_checks)
            overall_confidence = (decomposition.confidence + roadmap.confidence + avg_confidence) / 3
            
            reasoning_time = asyncio.get_event_loop().time() - start_time
            
            result = ReasoningResult(
                success=True,
                decomposition=decomposition,
                roadmap=roadmap,
                validation_checks=validation_checks,
                tracking_id=tracking_id,
                confidence=overall_confidence,
                reasoning_time=reasoning_time
            )
            
            # Store result
            self.active_reasonings[tracking_id] = result
            
            self.logger.info(f"Reasoning completed successfully in {reasoning_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Reasoning failed: {e}")
            return ReasoningResult(
                success=False,
                decomposition=None,
                roadmap=None,
                validation_checks=[],
                tracking_id=None,
                confidence=0.0,
                reasoning_time=asyncio.get_event_loop().time() - start_time,
                error_message=str(e)
            )
    
    async def update_reasoning_progress(self, tracking_id: str, step_id: str, 
                                      progress: float, notes: str = "") -> TrackStatus:
        """Update progress on an active reasoning/execution"""
        
        if tracking_id not in self.active_reasonings:
            self.logger.error(f"Unknown tracking ID: {tracking_id}")
            return TrackStatus.LOST
        
        status = self.track_keeper.update_progress(tracking_id, step_id, progress, notes)
        
        # Handle status changes
        if status == TrackStatus.MAJOR_DEVIATION or status == TrackStatus.LOST:
            self.logger.warning(f"Tracking {tracking_id} is off track: {status}")
            suggestions = self.track_keeper.get_recovery_suggestions(tracking_id)
            self.logger.info(f"Recovery suggestions: {suggestions}")
        
        return status
    
    async def check_reasoning_alignment(self, tracking_id: str, current_action: str, 
                                      expected_step: str) -> Dict[str, Any]:
        """Check if current action aligns with reasoning plan"""
        
        if tracking_id not in self.active_reasonings:
            return {
                "aligned": False,
                "confidence": 0.0,
                "message": "Unknown tracking ID",
                "suggestions": ["Restart reasoning process"]
            }
        
        confused, message, suggestions = self.track_keeper.detect_confusion(
            tracking_id, current_action, expected_step
        )
        
        return {
            "aligned": not confused,
            "confidence": 0.8 if not confused else 0.2,
            "message": message,
            "suggestions": suggestions
        }
    
    def get_reasoning_summary(self, tracking_id: str) -> Optional[Dict]:
        """Get summary of reasoning and progress"""
        
        if tracking_id not in self.active_reasonings:
            return None
        
        result = self.active_reasonings[tracking_id]
        tracking_summary = self.track_keeper.get_tracking_summary(tracking_id)
        
        return {
            "reasoning_result": {
                "success": result.success,
                "confidence": result.confidence,
                "reasoning_time": result.reasoning_time,
                "task": result.decomposition.original_task if result.decomposition else None,
                "subtasks_count": len(result.decomposition.subtasks) if result.decomposition else 0,
                "roadmap_steps": len(result.roadmap.steps) if result.roadmap else 0,
                "validation_issues": len([c for c in result.validation_checks if c.result.value != "pass"])
            },
            "tracking": tracking_summary,
            "validation_summary": {
                "total_checks": len(result.validation_checks),
                "passed": len([c for c in result.validation_checks if c.result.value == "pass"]),
                "warnings": len([c for c in result.validation_checks if c.result.value == "warning"]),
                "failed": len([c for c in result.validation_checks if c.result.value == "fail"])
            }
        }
    
    def list_active_reasonings(self) -> List[str]:
        """List all active reasoning tracking IDs"""
        return list(self.active_reasonings.keys())
    
    async def complete_reasoning(self, tracking_id: str) -> bool:
        """Mark reasoning as completed and clean up"""
        
        if tracking_id not in self.active_reasonings:
            return False
        
        # Update tracking status
        self.track_keeper.update_progress(tracking_id, "completed", 100.0, "Reasoning completed")
        
        # Clean up
        del self.active_reasonings[tracking_id]
        self.track_keeper.cleanup_tracking(tracking_id)
        
        self.logger.info(f"Completed reasoning {tracking_id}")
        return True
    
    async def recover_reasoning(self, tracking_id: str, checkpoint_id: str) -> bool:
        """Recover reasoning from a previous checkpoint"""
        
        if tracking_id not in self.active_reasonings:
            self.logger.error(f"Unknown tracking ID: {tracking_id}")
            return False
        
        success = self.track_keeper.backtrack_to_checkpoint(tracking_id, checkpoint_id)
        
        if success:
            self.logger.info(f"Successfully recovered reasoning {tracking_id} to checkpoint {checkpoint_id}")
        else:
            self.logger.error(f"Failed to recover reasoning {tracking_id}")
        
        return success
    
    async def llm_reason(self, prompt: str, system_prompt: Optional[str] = None, 
                        provider: Optional[str] = None) -> LLMResponse:
        """Use LLM for reasoning tasks"""
        try:
            response = await self.llm_manager.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                provider=provider
            )
            self.logger.info(f"LLM reasoning completed using {response.provider}")
            return response
        except Exception as e:
            self.logger.error(f"LLM reasoning failed: {e}")
            raise
    
    async def llm_chat(self, messages: List[Dict[str, str]], 
                      provider: Optional[str] = None) -> LLMResponse:
        """Use LLM for conversational reasoning"""
        try:
            response = await self.llm_manager.chat(
                messages=messages,
                provider=provider
            )
            self.logger.info(f"LLM chat completed using {response.provider}")
            return response
        except Exception as e:
            self.logger.error(f"LLM chat failed: {e}")
            raise

# Global reasoning engine instance
reasoning_engine = ReasoningEngine()
