"""
Test suite for Layer 1 Foundation components
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path

# Import our components
from core.memory.memory_manager import MemoryManager
from modules.tools.base_tool import ToolRegistry
from modules.tools.terminal_executor import TerminalExecutor
from modules.tools.file_manager import FileManager
from modules.tools.web_search import WebSearch
from modules.tools.calculator import Calculator
from modules.tools.human_input import HumanInput

async def test_memory_manager():
    """Test memory manager functionality"""
    print("🧠 Testing Memory Manager...")
    
    memory_manager = MemoryManager()
    await memory_manager.initialize()
    
    # Store a memory
    memory_id = await memory_manager.store_memory(
        content="Test memory for JARVIS development",
        memory_type="development",
        importance=0.8
    )
    
    # Retrieve memories
    memories = await memory_manager.retrieve_memories("JARVIS development")
    
    assert len(memories) > 0, "Should retrieve stored memory"
    assert memories[0].content == "Test memory for JARVIS development"
    
    print("✅ Memory Manager tests passed")

async def test_tool_registry():
    """Test tool registry and all tools"""
    print("🔧 Testing Tool Registry...")
    
    registry = ToolRegistry()
    
    # Register all tools
    tools = [
        TerminalExecutor(),
        FileManager(),
        WebSearch(),
        Calculator(),
        HumanInput()
    ]
    
    for tool in tools:
        registry.register_tool(tool)
    
    # Test tool listing
    tool_names = registry.list_tools()
    expected_tools = ["terminal_executor", "file_manager", "web_search", "calculator", "human_input"]
    
    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} should be registered"
    
    print("✅ Tool Registry tests passed")

async def test_terminal_executor():
    """Test terminal executor"""
    print("💻 Testing Terminal Executor...")
    
    executor = TerminalExecutor()
    
    # Test safe command
    result = await executor.safe_execute(command="echo 'Hello JARVIS'")
    assert result.success, "Safe command should succeed"
    assert "Hello JARVIS" in result.output["stdout"]
    
    # Test dangerous command blocking
    result = await executor.safe_execute(command="rm -rf /")
    assert not result.success, "Dangerous command should be blocked"
    
    print("✅ Terminal Executor tests passed")

async def test_file_manager():
    """Test file manager"""
    print("📁 Testing File Manager...")
    
    file_manager = FileManager()
    
    # Create test directory
    test_dir = "/tmp/jarvis_workspace/test"
    result = await file_manager.safe_execute(operation="create_dir", path=test_dir)
    assert result.success, f"Should create directory: {result.error_message}"
    
    # Write test file
    test_file = os.path.join(test_dir, "test.txt")
    result = await file_manager.safe_execute(
        operation="write", 
        path=test_file, 
        content="Test content"
    )
    assert result.success, f"Should write file: {result.error_message}"
    
    # Read test file
    result = await file_manager.safe_execute(operation="read", path=test_file)
    assert result.success, f"Should read file: {result.error_message}"
    assert result.output == "Test content"
    
    # Clean up
    result = await file_manager.safe_execute(operation="delete", path=test_dir)
    assert result.success, f"Should delete directory: {result.error_message}"
    
    print("✅ File Manager tests passed")

async def test_calculator():
    """Test calculator"""
    print("🧮 Testing Calculator...")
    
    calculator = Calculator()
    
    # Test basic arithmetic
    result = await calculator.safe_execute(expression="2 + 3 * 4")
    assert result.success, "Should calculate expression"
    assert result.output == 14
    
    # Test function
    result = await calculator.safe_execute(expression="sqrt(16)")
    assert result.success, "Should calculate sqrt"
    assert result.output == 4.0
    
    # Test dangerous expression blocking
    result = await calculator.safe_execute(expression="import os")
    assert not result.success, "Should block dangerous expression"
    
    print("✅ Calculator tests passed")

async def test_human_input():
    """Test human input tool"""
    print("👤 Testing Human Input...")
    
    human_input = HumanInput()
    
    # Test confirmation
    result = await human_input.safe_execute(
        prompt="Should we proceed with safe operation?",
        input_type="confirmation"
    )
    assert result.success, "Should get human input"
    assert result.output in ["yes", "no"]
    
    print("✅ Human Input tests passed")

async def run_all_tests():
    """Run all Layer 1 tests"""
    print("🚀 Running Layer 1 Foundation Tests")
    print("=" * 50)
    
    try:
        await test_memory_manager()
        await test_tool_registry()
        await test_terminal_executor()
        await test_file_manager()
        await test_calculator()
        await test_human_input()
        
        print("\n" + "=" * 50)
        print("🎉 ALL LAYER 1 TESTS PASSED!")
        print("✅ Foundation infrastructure is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
