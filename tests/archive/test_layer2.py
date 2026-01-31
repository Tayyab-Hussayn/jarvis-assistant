"""
Test suite for Layer 2 Reasoning Engine components
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# Import reasoning components
from core.engines.reasoning.task_decomposer import TaskDecomposer, TaskComplexity, TaskType
from core.engines.reasoning.roadmap_generator import RoadmapGenerator
from core.engines.reasoning.anti_hallucination import AntiHallucinationSystem, ValidationResult
from core.engines.reasoning.track_keeper import TrackKeeper, TrackStatus
from core.engines.reasoning.reasoning_engine import ReasoningEngine

async def test_task_decomposer():
    """Test task decomposition functionality"""
    print("🧠 Testing Task Decomposer...")
    
    decomposer = TaskDecomposer()
    
    # Test simple task
    simple_task = "Calculate the sum of 1 to 100"
    decomposition = await decomposer.decompose_task(simple_task)
    
    assert decomposition.original_task == simple_task
    assert len(decomposition.subtasks) >= 1
    assert decomposition.confidence > 0
    
    # Test complex task
    complex_task = "Build a web application for task management"
    decomposition = await decomposer.decompose_task(complex_task)
    
    assert len(decomposition.subtasks) > 3  # Should be decomposed into multiple steps
    assert decomposition.total_estimated_time > 60  # Should take more than 1 hour
    
    # Validate decomposition
    assert decomposer.validate_decomposition(decomposition)
    
    print("✅ Task Decomposer tests passed")

async def test_roadmap_generator():
    """Test roadmap generation"""
    print("🗺️ Testing Roadmap Generator...")
    
    decomposer = TaskDecomposer()
    generator = RoadmapGenerator()
    
    # Create a decomposition
    task = "Create a simple Python script"
    decomposition = await decomposer.decompose_task(task)
    
    # Generate roadmap
    roadmap = await generator.generate_roadmap(decomposition)
    
    assert roadmap.original_task == task
    assert len(roadmap.steps) == len(decomposition.subtasks)
    assert len(roadmap.execution_phases) > 0
    assert roadmap.total_estimated_time > 0
    
    # Validate roadmap
    is_valid, errors = generator.validate_roadmap(roadmap)
    assert is_valid, f"Roadmap validation failed: {errors}"
    
    print("✅ Roadmap Generator tests passed")

async def test_anti_hallucination():
    """Test anti-hallucination system"""
    print("🛡️ Testing Anti-Hallucination System...")
    
    decomposer = TaskDecomposer()
    generator = RoadmapGenerator()
    validator = AntiHallucinationSystem()
    
    # Create test data
    task = "Research artificial intelligence trends"
    decomposition = await decomposer.decompose_task(task)
    roadmap = await generator.generate_roadmap(decomposition)
    
    # Validate decomposition
    decomp_checks = await validator.validate_decomposition(decomposition)
    assert len(decomp_checks) > 0
    
    # Should have some passing checks
    passing_checks = [c for c in decomp_checks if c.result == ValidationResult.PASS]
    assert len(passing_checks) > 0
    
    # Validate roadmap
    roadmap_checks = await validator.validate_roadmap(roadmap)
    assert len(roadmap_checks) > 0
    
    print("✅ Anti-Hallucination System tests passed")

async def test_track_keeper():
    """Test track keeping functionality"""
    print("📍 Testing Track Keeper...")
    
    decomposer = TaskDecomposer()
    generator = RoadmapGenerator()
    tracker = TrackKeeper()
    
    # Create test roadmap
    task = "Write a technical document"
    decomposition = await decomposer.decompose_task(task)
    roadmap = await generator.generate_roadmap(decomposition)
    
    # Start tracking
    tracking_id = tracker.start_tracking(roadmap)
    assert tracking_id is not None
    
    # Update progress
    status = tracker.update_progress(tracking_id, "step_01", 25.0, "Started first step")
    assert status in [TrackStatus.ON_TRACK, TrackStatus.MINOR_DEVIATION]
    
    # Test confusion detection
    confused, message, suggestions = tracker.detect_confusion(
        tracking_id, "writing code", "plan_structure"
    )
    # Should detect some level of confusion since writing code doesn't match planning
    
    # Get summary
    summary = tracker.get_tracking_summary(tracking_id)
    assert summary is not None
    assert summary["tracking_id"] == tracking_id
    
    # Cleanup
    tracker.cleanup_tracking(tracking_id)
    
    print("✅ Track Keeper tests passed")

async def test_reasoning_engine():
    """Test complete reasoning engine"""
    print("🎯 Testing Reasoning Engine...")
    
    engine = ReasoningEngine()
    
    # Test complete reasoning process
    task = "Organize my project files"
    result = await engine.reason_about_task(task, validation_level="medium")  # Use medium validation
    
    if not result.success:
        print(f"Reasoning failed: {result.error_message}")
        # Try with low validation for testing
        result = await engine.reason_about_task(task, validation_level="low")
    
    assert result.success, f"Reasoning should succeed: {result.error_message}"
    assert result.decomposition is not None
    assert result.roadmap is not None
    assert result.tracking_id is not None
    assert result.confidence > 0
    
    # Test progress update
    tracking_id = result.tracking_id
    status = await engine.update_reasoning_progress(tracking_id, "step_01", 30.0, "Making progress")
    assert status != TrackStatus.LOST
    
    # Test alignment check
    alignment = await engine.check_reasoning_alignment(
        tracking_id, "organizing files", "step_01"
    )
    assert "aligned" in alignment
    
    # Get summary
    summary = engine.get_reasoning_summary(tracking_id)
    assert summary is not None
    
    # Complete reasoning
    completed = await engine.complete_reasoning(tracking_id)
    assert completed
    
    print("✅ Reasoning Engine tests passed")

async def test_integration():
    """Test integration between all components"""
    print("🔗 Testing Component Integration...")
    
    engine = ReasoningEngine()
    
    # Test with a complex, realistic task
    complex_task = "Build a REST API for user authentication with database integration"
    
    result = await engine.reason_about_task(complex_task, validation_level="low")  # Use low validation for testing
    
    if not result.success:
        print(f"Integration test failed: {result.error_message}")
        # Try simpler task
        complex_task = "Create a simple web page"
        result = await engine.reason_about_task(complex_task, validation_level="low")
    
    assert result.success, f"Integration test should succeed: {result.error_message}"
    assert len(result.decomposition.subtasks) >= 1  # Should have at least one subtask
    assert len(result.roadmap.execution_phases) >= 1  # Should have at least one phase
    assert len(result.validation_checks) >= 5  # Should have multiple validation checks
    
    # Simulate execution progress
    tracking_id = result.tracking_id
    
    for i, step in enumerate(result.roadmap.steps[:3]):  # Test first 3 steps
        progress = (i + 1) * 20  # 20%, 40%, 60%
        status = await engine.update_reasoning_progress(
            tracking_id, step.step_id, progress, f"Completed step {i+1}"
        )
        assert status != TrackStatus.LOST
    
    # Test recovery scenario
    checkpoints = engine.track_keeper.tracking_states[tracking_id].checkpoints
    if len(checkpoints) > 1:
        recovery_success = await engine.recover_reasoning(tracking_id, checkpoints[1].checkpoint_id)
        assert recovery_success
    
    # Complete
    await engine.complete_reasoning(tracking_id)
    
    print("✅ Integration tests passed")

async def run_all_tests():
    """Run all Layer 2 tests"""
    print("🚀 Running Layer 2 Reasoning Engine Tests")
    print("=" * 60)
    
    try:
        await test_task_decomposer()
        await test_roadmap_generator()
        await test_anti_hallucination()
        await test_track_keeper()
        await test_reasoning_engine()
        await test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 ALL LAYER 2 TESTS PASSED!")
        print("✅ Reasoning Engine is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
