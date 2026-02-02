#!/usr/bin/env python3
"""
JARVIS Demo - Show unified capabilities
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and show output"""
    print(f"\n🔧 Running: {cmd}")
    print("=" * 50)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/krawin/exp.code/jarvis")
    print(result.stdout)
    if result.stderr and "Environment variable" not in result.stderr:
        print("Errors:", result.stderr)

def main():
    """Demo JARVIS unified capabilities"""
    
    print("🤖 JARVIS Unified Interface Demo")
    print("=" * 60)
    
    # Show welcome
    run_command("./jarvis")
    
    # Show capabilities
    run_command("./jarvis capabilities --category 'Core Engines'")
    
    # Show status
    run_command("./jarvis status")
    
    # Show tools
    run_command("./jarvis tools list")
    
    # Show workflow status
    run_command("./jarvis workflow status")
    
    print("\n🎉 JARVIS Unified Interface Demo Complete!")
    print("✅ All capabilities accessible through single './jarvis' command")

if __name__ == "__main__":
    main()
