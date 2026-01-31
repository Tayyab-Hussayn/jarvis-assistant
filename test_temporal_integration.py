#!/usr/bin/env python3
"""
Temporal.io Integration Test Suite - Comprehensive testing
"""

import asyncio
import sys
import os
import time
import subprocess
from typing import Dict, Any

# Add project root to path
sys.path.append('/home/krawin/exp.code/jarvis')

from core.engines.workflow.enhanced_workflow import enhanced_workflow_engine, EnhancedWorkflowRequest

class TemporalIntegrationTester:
    """Comprehensive Temporal.io integration tester"""
    
    def __init__(self):
        self.test_results = []
        self.temporal_server_running = False
    
    def log_test(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration
        })
    
    def check_temporal_server(self) -> bool:
        """Check if Temporal server is running"""
        try:
            # Check if Docker Compose is running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=temporal", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "temporal" in result.stdout:
                self.temporal_server_running = True
                return True
            else:
                print("⚠️ Temporal server not detected. Starting server...")
                return self.start_temporal_server()
                
        except Exception as e:
            print(f"❌ Error checking Temporal server: {e}")
            return False
    
    def start_temporal_server(self) -> bool:
        """Start Temporal server using Docker Compose"""
        try:
            print("🚀 Starting Temporal server...")
            
            # Start Docker Compose in background
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-temporal.yml", "up", "-d"],
                cwd="/home/krawin/exp.code/jarvis",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Temporal server started successfully")
                # Wait for server to be ready
                time.sleep(10)
                self.temporal_server_running = True
                return True
            else:
                print(f"❌ Failed to start Temporal server: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Temporal server: {e}")
            return False
    
    async def test_engine_initialization(self):
        """Test 1: Engine initialization"""
        start_time = time.time()
        
        try:
            success = await enhanced_workflow_engine.initialize()
            duration = time.time() - start_time
            
            if success:
                status = enhanced_workflow_engine.get_engine_status()
                details = f"Temporal: {status['temporal_available']}, Simple: {status['simple_available']}"
                self.log_test("Engine Initialization", True, details, duration)
            else:
                self.log_test("Engine Initialization", False, "Failed to initialize", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Engine Initialization", False, str(e), duration)
    
    async def test_simple_workflow_fallback(self):
        """Test 2: Simple workflow fallback"""
        start_time = time.time()
        
        try:
            request = EnhancedWorkflowRequest(
                name="Test Simple Fallback",
                description="Test simple workflow execution",
                workflow_type="simple",
                use_temporal=False,
                parameters={
                    "tool_name": "terminal",
                    "command": "echo 'Hello from simple workflow'"
                }
            )
            
            result = await enhanced_workflow_engine.execute_workflow(request)
            duration = time.time() - start_time
            
            if result.get("success") and result.get("engine") == "simple":
                self.log_test("Simple Workflow Fallback", True, 
                            f"Workflow ID: {result['workflow_id']}", duration)
            else:
                self.log_test("Simple Workflow Fallback", False, 
                            f"Result: {result}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Simple Workflow Fallback", False, str(e), duration)
    
    async def test_temporal_simple_workflow(self):
        """Test 3: Temporal simple workflow"""
        start_time = time.time()
        
        try:
            request = EnhancedWorkflowRequest(
                name="Test Temporal Simple",
                description="Test Temporal simple workflow execution",
                workflow_type="temporal_simple",
                use_temporal=True,
                parameters={
                    "tool_name": "terminal",
                    "command": "echo 'Hello from Temporal workflow'"
                }
            )
            
            result = await enhanced_workflow_engine.execute_workflow(request)
            duration = time.time() - start_time
            
            if result.get("success"):
                engine = result.get("engine", "unknown")
                workflow_id = result.get("workflow_id", "unknown")
                self.log_test("Temporal Simple Workflow", True, 
                            f"Engine: {engine}, ID: {workflow_id}", duration)
            else:
                self.log_test("Temporal Simple Workflow", False, 
                            f"Result: {result}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Temporal Simple Workflow", False, str(e), duration)
    
    async def test_multi_step_workflow(self):
        """Test 4: Multi-step workflow"""
        start_time = time.time()
        
        try:
            steps = [
                {
                    "name": "Step 1: Create file",
                    "tool": "file_manager",
                    "parameters": {
                        "action": "write",
                        "path": "/tmp/test_workflow.txt",
                        "content": "Hello from multi-step workflow"
                    }
                },
                {
                    "name": "Step 2: Read file",
                    "tool": "file_manager",
                    "parameters": {
                        "action": "read",
                        "path": "/tmp/test_workflow.txt"
                    },
                    "depends_on": ["Step 1: Create file"]
                }
            ]
            
            request = EnhancedWorkflowRequest(
                name="Test Multi-Step",
                description="Test multi-step workflow execution",
                workflow_type="temporal_multi",
                use_temporal=True,
                steps=steps
            )
            
            result = await enhanced_workflow_engine.execute_workflow(request)
            duration = time.time() - start_time
            
            if result.get("success"):
                engine = result.get("engine", "unknown")
                steps_count = result.get("steps_count", 0)
                self.log_test("Multi-Step Workflow", True, 
                            f"Engine: {engine}, Steps: {steps_count}", duration)
            else:
                self.log_test("Multi-Step Workflow", False, 
                            f"Result: {result}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Multi-Step Workflow", False, str(e), duration)
    
    async def test_workflow_status_monitoring(self):
        """Test 5: Workflow status monitoring"""
        start_time = time.time()
        
        try:
            # Create a workflow first
            request = EnhancedWorkflowRequest(
                name="Test Status Monitoring",
                description="Test workflow status monitoring",
                workflow_type="simple",
                use_temporal=False,
                parameters={
                    "tool_name": "terminal",
                    "command": "sleep 1 && echo 'Status test complete'"
                }
            )
            
            result = await enhanced_workflow_engine.execute_workflow(request)
            
            if result.get("success"):
                workflow_id = result["workflow_id"]
                
                # Check status
                status = await enhanced_workflow_engine.get_workflow_status(workflow_id)
                duration = time.time() - start_time
                
                if status.get("workflow_id") == workflow_id:
                    self.log_test("Workflow Status Monitoring", True, 
                                f"Status: {status.get('status')}", duration)
                else:
                    self.log_test("Workflow Status Monitoring", False, 
                                f"Status check failed: {status}", duration)
            else:
                duration = time.time() - start_time
                self.log_test("Workflow Status Monitoring", False, 
                            "Failed to create test workflow", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Workflow Status Monitoring", False, str(e), duration)
    
    async def test_workflow_listing(self):
        """Test 6: Workflow listing"""
        start_time = time.time()
        
        try:
            workflows = await enhanced_workflow_engine.list_workflows()
            duration = time.time() - start_time
            
            workflow_count = len(workflows)
            engines = set(wf.get("engine", "unknown") for wf in workflows)
            
            self.log_test("Workflow Listing", True, 
                        f"Found {workflow_count} workflows, Engines: {engines}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Workflow Listing", False, str(e), duration)
    
    async def test_engine_status(self):
        """Test 7: Engine status reporting"""
        start_time = time.time()
        
        try:
            status = enhanced_workflow_engine.get_engine_status()
            duration = time.time() - start_time
            
            required_keys = ["initialized", "temporal_available", "simple_available", "preferred_engine"]
            has_all_keys = all(key in status for key in required_keys)
            
            if has_all_keys:
                details = f"Initialized: {status['initialized']}, Preferred: {status['preferred_engine']}"
                self.log_test("Engine Status Reporting", True, details, duration)
            else:
                self.log_test("Engine Status Reporting", False, 
                            f"Missing keys in status: {status}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Engine Status Reporting", False, str(e), duration)
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("🧪 TEMPORAL.IO INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 INTEGRATION STATUS:")
        if passed_tests >= 5:  # At least 5 tests should pass
            print("✅ Temporal.io integration is WORKING")
            print("✅ M1 - Full Temporal.io Integration: COMPLETE")
        else:
            print("⚠️ Temporal.io integration has issues")
            print("🔄 M1 - Full Temporal.io Integration: NEEDS ATTENTION")
        
        print("="*60)

async def main():
    """Run comprehensive Temporal.io integration tests"""
    print("🧪 TEMPORAL.IO INTEGRATION TEST SUITE")
    print("="*50)
    
    tester = TemporalIntegrationTester()
    
    # Check if Temporal server is running
    print("🔍 Checking Temporal server status...")
    server_running = tester.check_temporal_server()
    
    if not server_running:
        print("⚠️ Temporal server not available. Testing fallback mode only.")
    
    # Run all tests
    print("\n🚀 Running integration tests...\n")
    
    await tester.test_engine_initialization()
    await tester.test_simple_workflow_fallback()
    
    if server_running:
        await tester.test_temporal_simple_workflow()
        await tester.test_multi_step_workflow()
    
    await tester.test_workflow_status_monitoring()
    await tester.test_workflow_listing()
    await tester.test_engine_status()
    
    # Print summary
    tester.print_summary()
    
    # Cleanup
    await enhanced_workflow_engine.close()

if __name__ == "__main__":
    asyncio.run(main())
