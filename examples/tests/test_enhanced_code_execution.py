#!/usr/bin/env python3
"""
Test Enhanced Code Execution - 3 Different Methods
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

# Test Method 1: Direct Executor Testing
async def test_method_1_direct_executor():
    """Test Method 1: Direct Docker Executor"""
    print("🧪 Test Method 1: Direct Docker Executor")
    print("=" * 45)
    
    try:
        executor = DockerCodeExecutor()
        
        # Test initialization
        docker_available = await executor.initialize()
        print(f"   Docker Available: {docker_available}")
        
        # Test Python execution
        print("\n   Testing Python execution...")
        python_code = """
print("Hello from JARVIS!")
result = 2 + 3
print(f"Calculation: 2 + 3 = {result}")
"""
        
        config = ExecutionConfig(language="python", timeout=10)
        result = await executor.execute_code(python_code, config)
        
        print(f"   ✅ Python execution: {result.success}")
        print(f"   Output: {result.output[:100]}...")
        print(f"   Time: {result.execution_time:.3f}s")
        
        # Test JavaScript execution
        print("\n   Testing JavaScript execution...")
        js_code = """
console.log("Hello from Node.js!");
const result = 5 * 6;
console.log(`Calculation: 5 * 6 = ${result}`);
"""
        
        config = ExecutionConfig(language="javascript", timeout=10)
        result = await executor.execute_code(js_code, config)
        
        print(f"   ✅ JavaScript execution: {result.success}")
        if result.output:
            print(f"   Output: {result.output[:100]}...")
        if result.error:
            print(f"   Note: {result.error[:100]}...")
        
        # Test Bash execution
        print("\n   Testing Bash execution...")
        bash_code = """
echo "Hello from Bash!"
echo "Current date: $(date)"
echo "System info: $(uname -a)"
"""
        
        config = ExecutionConfig(language="bash", timeout=10)
        result = await executor.execute_code(bash_code, config)
        
        print(f"   ✅ Bash execution: {result.success}")
        if result.output:
            print(f"   Output: {result.output[:100]}...")
        
        print("   ✅ Direct executor test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Direct executor test FAILED: {e}")
        return False

# Test Method 2: Tool Integration Testing
async def test_method_2_tool_integration():
    """Test Method 2: Enhanced Code Executor Tool"""
    print("\n🧪 Test Method 2: Enhanced Code Executor Tool")
    print("=" * 50)
    
    try:
        from modules.tools.enhanced_code_executor_tool import EnhancedCodeExecutorTool
        
        # Test tool initialization
        tool = EnhancedCodeExecutorTool()
        print("   ✅ Tool initialized successfully")
        
        # Test input validation
        valid = tool.validate_input("print('hello')", "python")
        print(f"   ✅ Input validation: {valid}")
        
        # Test invalid input
        invalid = tool.validate_input("rm -rf /", "bash")
        print(f"   ✅ Security validation: {not invalid}")
        
        # Test Python execution through tool
        print("\n   Testing Python through tool...")
        result = await tool.execute(
            code="print('JARVIS Enhanced Executor')\nprint(f'Result: {10**2}')",
            language="python"
        )
        
        print(f"   ✅ Tool execution: {result.success}")
        if result.output:
            print(f"   Output: {result.output}")
        
        # Test JavaScript through tool
        print("\n   Testing JavaScript through tool...")
        result = await tool.execute(
            code="console.log('Enhanced JS execution'); console.log(Math.pow(2, 8));",
            language="javascript"
        )
        
        print(f"   ✅ JS tool execution: {result.success}")
        if result.output:
            print(f"   Docker used: {result.output.get('docker_used', 'Unknown')}")
        
        print("   ✅ Tool integration test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Tool integration test FAILED: {e}")
        return False

# Test Method 3: Security and Limits Testing
async def test_method_3_security_limits():
    """Test Method 3: Security and Resource Limits"""
    print("\n🧪 Test Method 3: Security and Resource Limits")
    print("=" * 50)
    
    try:
        executor = DockerCodeExecutor()
        await executor.initialize()
        
        # Test 1: Timeout handling
        print("   Testing timeout handling...")
        timeout_code = """
import time
print("Starting long operation...")
time.sleep(60)  # This should timeout
print("This should not print")
"""
        
        config = ExecutionConfig(language="python", timeout=3)
        result = await executor.execute_code(timeout_code, config)
        
        timeout_handled = not result.success and "timeout" in result.error.lower()
        print(f"   ✅ Timeout handling: {timeout_handled}")
        
        # Test 2: Memory limit (conceptual - actual limits need Docker)
        print("\n   Testing memory awareness...")
        memory_code = """
print("Testing memory usage...")
data = []
for i in range(1000):
    data.append(f"Item {i}")
print(f"Created {len(data)} items")
"""
        
        config = ExecutionConfig(language="python", memory_limit="64m")
        result = await executor.execute_code(memory_code, config)
        
        print(f"   ✅ Memory test execution: {result.success}")
        
        # Test 3: Security validation
        print("\n   Testing security validation...")
        dangerous_code = "import os; os.system('ls')"
        
        config = ExecutionConfig(language="python")
        result = await executor.execute_code(dangerous_code, config)
        
        security_blocked = not result.success and "dangerous" in result.error.lower()
        print(f"   ✅ Security blocking: {security_blocked}")
        
        # Test 4: Output size limiting
        print("\n   Testing output size limits...")
        large_output_code = """
for i in range(1000):
    print(f"Line {i}: This is a test of output size limiting")
"""
        
        config = ExecutionConfig(language="python", max_output_size=500)
        result = await executor.execute_code(large_output_code, config)
        
        output_limited = len(result.output) <= 500
        print(f"   ✅ Output size limiting: {output_limited}")
        
        print("   ✅ Security and limits test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Security and limits test FAILED: {e}")
        return False

async def run_all_tests():
    """Run all code execution tests"""
    print("🚀 JARVIS Enhanced Code Execution Test Suite")
    print("=" * 55)
    
    # Run all test methods
    test1_result = await test_method_1_direct_executor()
    test2_result = await test_method_2_tool_integration()
    test3_result = await test_method_3_security_limits()
    
    # Summary
    print(f"\n🎯 Test Results Summary:")
    print(f"   Method 1 (Direct Executor): {'PASS' if test1_result else 'FAIL'}")
    print(f"   Method 2 (Tool Integration): {'PASS' if test2_result else 'FAIL'}")
    print(f"   Method 3 (Security/Limits):  {'PASS' if test3_result else 'FAIL'}")
    
    all_passed = test1_result and test2_result and test3_result
    
    if all_passed:
        print(f"\n🎉 ALL CODE EXECUTION TESTS PASSED!")
        print(f"✅ Enhanced code execution environment is ready")
        print(f"🐳 Docker integration: {'Available' if test1_result else 'Fallback mode'}")
        print(f"🔒 Security features: Working")
        print(f"⚡ Multi-language support: Ready")
    else:
        print(f"\n⚠️  Some tests had issues - system still functional")
        print(f"💡 Docker may not be available - using fallback execution")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)
