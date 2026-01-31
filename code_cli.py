#!/usr/bin/env python3
"""
Code Execution CLI - Test enhanced code execution
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "test":
        await test_execution()
    elif command == "python":
        code = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "print('Hello from JARVIS!')"
        await execute_code(code, "python")
    elif command == "js":
        code = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "console.log('Hello from JARVIS!');"
        await execute_code(code, "javascript")
    elif command == "bash":
        code = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "echo 'Hello from JARVIS!'"
        await execute_code(code, "bash")
    else:
        print_help()

def print_help():
    """Print help information"""
    print("""
💻 JARVIS Code Execution CLI

Commands:
  test                 - Test code execution system
  python <code>        - Execute Python code
  js <code>           - Execute JavaScript code  
  bash <code>         - Execute Bash code
  
Examples:
  python code_cli.py test
  python code_cli.py python "print('Hello World')"
  python code_cli.py js "console.log('Hello');"
  python code_cli.py bash "echo 'Hello'"
""")

async def test_execution():
    """Test code execution system"""
    print("🧪 Testing JARVIS Code Execution System")
    print("=" * 45)
    
    executor = DockerCodeExecutor()
    docker_available = await executor.initialize()
    
    print(f"Docker Available: {docker_available}")
    
    # Test Python
    print("\n🐍 Testing Python:")
    python_result = await executor.execute_code(
        "print('Python execution working!')\nprint(f'2 + 2 = {2+2}')",
        ExecutionConfig(language="python")
    )
    print(f"   Success: {python_result.success}")
    print(f"   Output: {python_result.output}")
    if python_result.error:
        print(f"   Error: {python_result.error}")
    
    # Test JavaScript (fallback)
    print("\n🟨 Testing JavaScript:")
    js_result = await executor.execute_code(
        "console.log('JavaScript execution working!'); console.log('2 + 2 =', 2+2);",
        ExecutionConfig(language="javascript")
    )
    print(f"   Success: {js_result.success}")
    print(f"   Output: {js_result.output}")
    if js_result.error:
        print(f"   Error: {js_result.error}")
    
    # Test Bash
    print("\n🐚 Testing Bash:")
    bash_result = await executor.execute_code(
        "echo 'Bash execution working!'\necho 'Current user:' $(whoami)",
        ExecutionConfig(language="bash")
    )
    print(f"   Success: {bash_result.success}")
    print(f"   Output: {bash_result.output}")
    if bash_result.error:
        print(f"   Error: {bash_result.error}")
    
    print(f"\n🎉 Code execution system test complete!")

async def execute_code(code: str, language: str):
    """Execute code in specified language"""
    print(f"💻 Executing {language.title()} code:")
    print(f"Code: {code}")
    print("-" * 40)
    
    executor = DockerCodeExecutor()
    await executor.initialize()
    
    config = ExecutionConfig(language=language, timeout=10)
    result = await executor.execute_code(code, config)
    
    if result.success:
        print("✅ Execution successful!")
        print(f"Output:\n{result.output}")
    else:
        print("❌ Execution failed!")
        print(f"Error: {result.error}")
    
    print(f"Execution time: {result.execution_time:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())
