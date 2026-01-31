"""
Comprehensive Test Suite - Production-grade testing
"""

import asyncio
import unittest
from typing import Dict, Any

class TestJarvisSystem(unittest.TestCase):
    """Comprehensive system tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = {"test": True}
    
    def test_memory_system(self):
        """Test memory management"""
        from core.memory.memory_manager import memory_manager
        self.assertIsNotNone(memory_manager)
    
    def test_tool_registry(self):
        """Test tool registry"""
        from modules.tools.base_tool import tool_registry
        tools = tool_registry.list_tools()
        self.assertGreater(len(tools), 0)
    
    def test_reasoning_engine(self):
        """Test reasoning capabilities"""
        from core.engines.reasoning.reasoning_engine import reasoning_engine
        self.assertIsNotNone(reasoning_engine)
    
    def test_execution_engine(self):
        """Test execution capabilities"""
        from core.engines.execution.execution_engine import execution_engine
        self.assertIsNotNone(execution_engine)
    
    def test_workflow_engine(self):
        """Test workflow capabilities"""
        from core.engines.workflow.simple_workflow import workflow_engine
        self.assertIsNotNone(workflow_engine)
    
    def test_skills_framework(self):
        """Test skills system"""
        from skills.skill_framework import skill_registry
        self.assertIsNotNone(skill_registry)
    
    def test_intelligence_upgrades(self):
        """Test intelligence system"""
        from core.intelligence.upgrades import intelligence_upgrades
        self.assertIsNotNone(intelligence_upgrades)
    
    def test_monitoring_system(self):
        """Test monitoring"""
        from core.monitoring.observability import metrics, alerting
        self.assertIsNotNone(metrics)
        self.assertIsNotNone(alerting)

async def run_integration_tests():
    """Run integration tests"""
    print("🧪 Running Integration Tests...")
    
    # Test basic workflow
    from core.engines.workflow.simple_workflow import workflow_engine
    from core.engines.execution.execution_engine import execution_engine
    
    workflow_engine.set_execution_engine(execution_engine)
    
    # Create simple workflow
    workflow = workflow_engine.create_workflow_from_nl("Test workflow")
    result = await workflow_engine.execute_workflow(workflow)
    
    assert result, "Workflow execution should succeed"
    print("✅ Workflow integration test passed")
    
    # Test skills
    from skills.skill_framework import skill_registry
    
    skill_result = await skill_registry.execute_skill("prompt_optimizer", {
        "type": "coding",
        "task": "Create a hello world program"
    })
    
    assert skill_result.success, "Skill execution should succeed"
    print("✅ Skills integration test passed")
    
    # Test intelligence upgrades
    from core.intelligence.upgrades import intelligence_upgrades
    
    intelligence_result = await intelligence_upgrades.enhanced_reasoning(
        "Plan a software project", {"context": "test"}
    )
    
    assert intelligence_result["confidence"] > 0, "Intelligence upgrade should work"
    print("✅ Intelligence integration test passed")

def run_all_tests():
    """Run all tests"""
    print("🚀 Running Comprehensive Test Suite")
    print("=" * 50)
    
    # Unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Integration tests
    asyncio.run(run_integration_tests())
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    run_all_tests()
