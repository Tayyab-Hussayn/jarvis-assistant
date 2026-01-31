"""
Track Keeper - Prevents confusion and derailment during complex tasks
Maintains awareness of current position in roadmap and detects deviations
"""

import json
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

from .roadmap_generator import Roadmap, ExecutionStep

class TrackStatus(Enum):
    ON_TRACK = "on_track"
    MINOR_DEVIATION = "minor_deviation"
    MAJOR_DEVIATION = "major_deviation"
    LOST = "lost"
    COMPLETED = "completed"

@dataclass
class Checkpoint:
    checkpoint_id: str
    step_id: str
    timestamp: datetime
    status: TrackStatus
    progress_percentage: float
    notes: str
    
@dataclass
class TrackingState:
    roadmap_id: str
    current_step_id: Optional[str]
    current_phase: int
    completed_steps: List[str]
    checkpoints: List[Checkpoint]
    overall_progress: float
    status: TrackStatus
    last_update: datetime

class TrackKeeper:
    """Keep track of progress and prevent derailment"""
    
    def __init__(self):
        self.logger = logging.getLogger("track_keeper")
        self.tracking_states: Dict[str, TrackingState] = {}
        
    def start_tracking(self, roadmap: Roadmap) -> str:
        """Start tracking a roadmap execution"""
        
        tracking_id = f"track_{roadmap.roadmap_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize tracking state
        state = TrackingState(
            roadmap_id=roadmap.roadmap_id,
            current_step_id=None,
            current_phase=0,
            completed_steps=[],
            checkpoints=[],
            overall_progress=0.0,
            status=TrackStatus.ON_TRACK,
            last_update=datetime.now()
        )
        
        self.tracking_states[tracking_id] = state
        
        # Create initial checkpoint
        self.create_checkpoint(
            tracking_id, 
            "tracking_start", 
            TrackStatus.ON_TRACK, 
            0.0, 
            "Started tracking roadmap execution"
        )
        
        self.logger.info(f"Started tracking roadmap {roadmap.roadmap_id} as {tracking_id}")
        return tracking_id
    
    def create_checkpoint(self, tracking_id: str, step_id: str, status: TrackStatus, 
                         progress: float, notes: str = "") -> bool:
        """Create a checkpoint for current progress"""
        
        if tracking_id not in self.tracking_states:
            self.logger.error(f"Unknown tracking ID: {tracking_id}")
            return False
        
        state = self.tracking_states[tracking_id]
        
        checkpoint = Checkpoint(
            checkpoint_id=f"cp_{len(state.checkpoints)+1:03d}",
            step_id=step_id,
            timestamp=datetime.now(),
            status=status,
            progress_percentage=progress,
            notes=notes
        )
        
        state.checkpoints.append(checkpoint)
        state.last_update = datetime.now()
        
        self.logger.info(f"Created checkpoint {checkpoint.checkpoint_id} for {tracking_id}")
        return True
    
    def update_progress(self, tracking_id: str, step_id: str, progress: float, 
                       notes: str = "") -> TrackStatus:
        """Update progress and check if still on track"""
        
        if tracking_id not in self.tracking_states:
            self.logger.error(f"Unknown tracking ID: {tracking_id}")
            return TrackStatus.LOST
        
        state = self.tracking_states[tracking_id]
        
        # Update current step
        if state.current_step_id != step_id:
            if state.current_step_id:
                # Mark previous step as completed
                if state.current_step_id not in state.completed_steps:
                    state.completed_steps.append(state.current_step_id)
            
            state.current_step_id = step_id
        
        # Update overall progress
        state.overall_progress = progress
        
        # Determine status
        status = self._assess_track_status(tracking_id, step_id, progress)
        state.status = status
        
        # Create checkpoint
        self.create_checkpoint(tracking_id, step_id, status, progress, notes)
        
        return status
    
    def _assess_track_status(self, tracking_id: str, current_step_id: str, 
                           progress: float) -> TrackStatus:
        """Assess if execution is still on track"""
        
        state = self.tracking_states[tracking_id]
        
        # Simple heuristics for track assessment
        # In production, this would be more sophisticated
        
        # Check progress consistency
        if len(state.checkpoints) > 1:
            last_checkpoint = state.checkpoints[-1]
            progress_delta = progress - last_checkpoint.progress_percentage
            time_delta = (datetime.now() - last_checkpoint.timestamp).total_seconds() / 60  # minutes
            
            # Expected progress rate (rough estimate)
            expected_rate = 1.0  # 1% per minute (very rough)
            expected_progress = expected_rate * time_delta
            
            if progress_delta < expected_progress * 0.5:
                if progress_delta < expected_progress * 0.2:
                    return TrackStatus.MAJOR_DEVIATION
                else:
                    return TrackStatus.MINOR_DEVIATION
        
        # Check if making reasonable progress
        if progress >= 100.0:
            return TrackStatus.COMPLETED
        elif progress > 0:
            return TrackStatus.ON_TRACK
        else:
            return TrackStatus.MINOR_DEVIATION
    
    def detect_confusion(self, tracking_id: str, current_action: str, 
                        expected_step_id: str) -> Tuple[bool, str, List[str]]:
        """Detect if current action matches expected step"""
        
        if tracking_id not in self.tracking_states:
            return True, "Unknown tracking ID", ["Restart tracking"]
        
        state = self.tracking_states[tracking_id]
        
        # Simple confusion detection based on action keywords
        action_lower = current_action.lower()
        
        # Get expected step details (would need roadmap reference in production)
        expected_keywords = self._get_step_keywords(expected_step_id)
        
        # Check if current action aligns with expected step
        alignment_score = self._calculate_alignment(action_lower, expected_keywords)
        
        if alignment_score > 0.7:
            return False, "Action aligns with expected step", []
        elif alignment_score > 0.3:
            return False, "Minor misalignment detected", [
                "Review current step requirements",
                "Ensure action matches step objectives"
            ]
        else:
            return True, "Major confusion detected - action doesn't match expected step", [
                "Stop current action",
                "Review roadmap and current position",
                "Restart from last checkpoint if needed"
            ]
    
    def _get_step_keywords(self, step_id: str) -> List[str]:
        """Get keywords associated with a step (simplified)"""
        # In production, this would reference the actual roadmap
        keyword_map = {
            "req_analysis": ["analyze", "requirements", "understand", "document"],
            "arch_design": ["design", "architecture", "plan", "structure"],
            "setup_env": ["setup", "environment", "install", "configure"],
            "core_impl": ["implement", "code", "build", "develop"],
            "testing": ["test", "verify", "validate", "check"],
            "deployment": ["deploy", "release", "production", "launch"]
        }
        
        return keyword_map.get(step_id, [])
    
    def _calculate_alignment(self, action: str, expected_keywords: List[str]) -> float:
        """Calculate alignment between action and expected keywords"""
        if not expected_keywords:
            return 0.5  # Neutral if no keywords
        
        action_words = set(action.split())
        expected_words = set(expected_keywords)
        
        intersection = action_words & expected_words
        union = action_words | expected_words
        
        if not union:
            return 0.5  # Neutral if no words to compare
        
        return len(intersection) / len(union)
    
    def get_recovery_suggestions(self, tracking_id: str) -> List[str]:
        """Get suggestions for getting back on track"""
        
        if tracking_id not in self.tracking_states:
            return ["Restart tracking system"]
        
        state = self.tracking_states[tracking_id]
        
        suggestions = []
        
        if state.status == TrackStatus.LOST:
            suggestions.extend([
                "Review original roadmap and objectives",
                "Identify last successful checkpoint",
                "Restart from last known good state",
                "Break down current confusion into smaller steps"
            ])
        elif state.status == TrackStatus.MAJOR_DEVIATION:
            suggestions.extend([
                "Pause current activity",
                "Review current step requirements",
                "Identify what caused the deviation",
                "Adjust approach to align with roadmap"
            ])
        elif state.status == TrackStatus.MINOR_DEVIATION:
            suggestions.extend([
                "Review current step objectives",
                "Make minor adjustments to stay on track",
                "Continue with increased awareness"
            ])
        
        return suggestions
    
    def backtrack_to_checkpoint(self, tracking_id: str, checkpoint_id: str) -> bool:
        """Backtrack to a previous checkpoint"""
        
        if tracking_id not in self.tracking_states:
            self.logger.error(f"Unknown tracking ID: {tracking_id}")
            return False
        
        state = self.tracking_states[tracking_id]
        
        # Find the checkpoint
        target_checkpoint = None
        for cp in state.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                target_checkpoint = cp
                break
        
        if not target_checkpoint:
            self.logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        # Reset state to checkpoint
        state.current_step_id = target_checkpoint.step_id
        state.overall_progress = target_checkpoint.progress_percentage
        state.status = TrackStatus.ON_TRACK
        
        # Remove checkpoints after the target
        checkpoint_index = state.checkpoints.index(target_checkpoint)
        state.checkpoints = state.checkpoints[:checkpoint_index + 1]
        
        # Create recovery checkpoint
        self.create_checkpoint(
            tracking_id,
            target_checkpoint.step_id,
            TrackStatus.ON_TRACK,
            target_checkpoint.progress_percentage,
            f"Backtracked to checkpoint {checkpoint_id}"
        )
        
        self.logger.info(f"Backtracked to checkpoint {checkpoint_id}")
        return True
    
    def get_tracking_summary(self, tracking_id: str) -> Optional[Dict]:
        """Get summary of tracking progress"""
        
        if tracking_id not in self.tracking_states:
            return None
        
        state = self.tracking_states[tracking_id]
        
        return {
            "tracking_id": tracking_id,
            "roadmap_id": state.roadmap_id,
            "current_step": state.current_step_id,
            "progress": state.overall_progress,
            "status": state.status.value,
            "completed_steps": len(state.completed_steps),
            "total_checkpoints": len(state.checkpoints),
            "last_update": state.last_update.isoformat(),
            "recent_checkpoints": [
                {
                    "id": cp.checkpoint_id,
                    "step": cp.step_id,
                    "progress": cp.progress_percentage,
                    "status": cp.status.value,
                    "notes": cp.notes
                }
                for cp in state.checkpoints[-3:]  # Last 3 checkpoints
            ]
        }
    
    def cleanup_tracking(self, tracking_id: str) -> bool:
        """Clean up completed tracking"""
        
        if tracking_id in self.tracking_states:
            del self.tracking_states[tracking_id]
            self.logger.info(f"Cleaned up tracking {tracking_id}")
            return True
        
        return False
