#!/usr/bin/env python3
"""
Temporal Workflow CLI - Command-line interface for workflow management
"""

import asyncio
import sys
import argparse
import json
from typing import Dict, Any

# Add project root to path
sys.path.append('/home/krawin/exp.code/jarvis')

from core.engines.workflow.enhanced_workflow import enhanced_workflow_engine, EnhancedWorkflowRequest

class TemporalWorkflowCLI:
    """Command-line interface for Temporal workflow management"""
    
    def __init__(self):
        self.engine = enhanced_workflow_engine
    
    async def initialize(self):
        """Initialize the workflow engine"""
        print("🔄 Initializing workflow engine...")
        success = await self.engine.initialize()
        
        if success:
            status = self.engine.get_engine_status()
            print("✅ Workflow engine initialized")
            print(f"   Temporal available: {status['temporal_available']}")
            print(f"   Preferred engine: {status['preferred_engine']}")
        else:
            print("❌ Failed to initialize workflow engine")
        
        return success
    
    async def create_simple_workflow(self, args):
        """Create and execute simple workflow"""
        print(f"🚀 Creating simple workflow: {args.name}")
        
        request = EnhancedWorkflowRequest(
            name=args.name,
            description=args.description or f"Simple workflow: {args.name}",
            workflow_type="temporal_simple" if args.use_temporal else "simple",
            use_temporal=args.use_temporal,
            parameters={
                "tool_name": args.tool,
                **self._parse_parameters(args.parameters)
            }
        )
        
        result = await self.engine.execute_workflow(request)
        
        if result.get("success"):
            print(f"✅ Workflow created successfully")
            print(f"   Workflow ID: {result['workflow_id']}")
            print(f"   Engine: {result['engine']}")
            print(f"   Status: {result.get('status', 'unknown')}")
        else:
            print(f"❌ Workflow creation failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    async def create_multi_step_workflow(self, args):
        """Create and execute multi-step workflow"""
        print(f"🚀 Creating multi-step workflow: {args.name}")
        
        # Parse steps from JSON file or command line
        steps = []
        if args.steps_file:
            try:
                with open(args.steps_file, 'r') as f:
                    steps = json.load(f)
            except Exception as e:
                print(f"❌ Failed to load steps file: {e}")
                return
        else:
            # Create simple two-step example
            steps = [
                {
                    "name": "Step 1",
                    "tool": "terminal",
                    "parameters": {"command": "echo 'Step 1 executed'"}
                },
                {
                    "name": "Step 2",
                    "tool": "terminal",
                    "parameters": {"command": "echo 'Step 2 executed'"},
                    "depends_on": ["Step 1"]
                }
            ]
        
        request = EnhancedWorkflowRequest(
            name=args.name,
            description=args.description or f"Multi-step workflow: {args.name}",
            workflow_type="temporal_multi" if args.use_temporal else "simple",
            use_temporal=args.use_temporal,
            steps=steps
        )
        
        result = await self.engine.execute_workflow(request)
        
        if result.get("success"):
            print(f"✅ Multi-step workflow created successfully")
            print(f"   Workflow ID: {result['workflow_id']}")
            print(f"   Engine: {result['engine']}")
            print(f"   Steps: {result.get('steps_count', len(steps))}")
        else:
            print(f"❌ Multi-step workflow creation failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    async def get_workflow_status(self, args):
        """Get workflow status"""
        print(f"🔍 Getting status for workflow: {args.workflow_id}")
        
        status = await self.engine.get_workflow_status(args.workflow_id)
        
        if status.get("status") != "not_found":
            print(f"✅ Workflow found")
            print(f"   ID: {status['workflow_id']}")
            print(f"   Engine: {status.get('engine', 'unknown')}")
            print(f"   Status: {status.get('status', 'unknown')}")
            
            if "start_time" in status:
                print(f"   Start Time: {status['start_time']}")
            if "execution_time" in status:
                print(f"   Execution Time: {status['execution_time']}")
        else:
            print(f"❌ Workflow not found: {args.workflow_id}")
    
    async def list_workflows(self, args):
        """List all workflows"""
        print("📋 Listing workflows...")
        
        workflows = await self.engine.list_workflows(args.engine)
        
        if workflows:
            print(f"✅ Found {len(workflows)} workflows:")
            for wf in workflows:
                print(f"   • {wf.get('workflow_id', 'unknown')} ({wf.get('engine', 'unknown')})")
                print(f"     Name: {wf.get('name', 'N/A')}")
                print(f"     Status: {wf.get('status', 'unknown')}")
        else:
            print("📭 No workflows found")
    
    async def cancel_workflow(self, args):
        """Cancel a workflow"""
        print(f"🛑 Cancelling workflow: {args.workflow_id}")
        
        success = await self.engine.cancel_workflow(args.workflow_id)
        
        if success:
            print(f"✅ Workflow cancelled successfully")
        else:
            print(f"❌ Failed to cancel workflow")
    
    async def show_engine_status(self, args):
        """Show engine status"""
        print("📊 Engine Status:")
        
        status = self.engine.get_engine_status()
        
        print(f"   Initialized: {status['initialized']}")
        print(f"   Temporal Available: {status['temporal_available']}")
        print(f"   Simple Available: {status['simple_available']}")
        print(f"   Preferred Engine: {status['preferred_engine']}")
    
    def _parse_parameters(self, param_string: str) -> Dict[str, Any]:
        """Parse parameter string into dictionary"""
        if not param_string:
            return {}
        
        try:
            # Try JSON format first
            return json.loads(param_string)
        except:
            # Fall back to key=value format
            params = {}
            for pair in param_string.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()
            return params

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Temporal Workflow CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simple workflow command
    simple_parser = subparsers.add_parser('simple', help='Create simple workflow')
    simple_parser.add_argument('name', help='Workflow name')
    simple_parser.add_argument('--description', help='Workflow description')
    simple_parser.add_argument('--tool', default='terminal', help='Tool to execute')
    simple_parser.add_argument('--parameters', help='Tool parameters (JSON or key=value)')
    simple_parser.add_argument('--use-temporal', action='store_true', help='Force use of Temporal')
    
    # Multi-step workflow command
    multi_parser = subparsers.add_parser('multi', help='Create multi-step workflow')
    multi_parser.add_argument('name', help='Workflow name')
    multi_parser.add_argument('--description', help='Workflow description')
    multi_parser.add_argument('--steps-file', help='JSON file with workflow steps')
    multi_parser.add_argument('--use-temporal', action='store_true', help='Force use of Temporal')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get workflow status')
    status_parser.add_argument('workflow_id', help='Workflow ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List workflows')
    list_parser.add_argument('--engine', choices=['temporal', 'simple'], help='Filter by engine')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel workflow')
    cancel_parser.add_argument('workflow_id', help='Workflow ID')
    
    # Engine status command
    subparsers.add_parser('engine-status', help='Show engine status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = TemporalWorkflowCLI()
    
    # Initialize engine
    if not await cli.initialize():
        print("❌ Failed to initialize. Exiting.")
        return
    
    # Execute command
    try:
        if args.command == 'simple':
            await cli.create_simple_workflow(args)
        elif args.command == 'multi':
            await cli.create_multi_step_workflow(args)
        elif args.command == 'status':
            await cli.get_workflow_status(args)
        elif args.command == 'list':
            await cli.list_workflows(args)
        elif args.command == 'cancel':
            await cli.cancel_workflow(args)
        elif args.command == 'engine-status':
            await cli.show_engine_status(args)
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await cli.engine.close()

if __name__ == "__main__":
    asyncio.run(main())
