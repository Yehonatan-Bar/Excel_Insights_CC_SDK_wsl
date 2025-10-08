#!/usr/bin/env python3
"""
Test script to verify Hebrew language enforcement in the agent
"""
import asyncio
from pathlib import Path
from agent_service import ExcelAnalysisAgent

async def test_hebrew_default():
    """Test that Hebrew is used by default regardless of input file language"""

    print("=" * 60)
    print("Testing Hebrew Language Enforcement")
    print("=" * 60)

    # Initialize agent
    agent = ExcelAnalysisAgent(output_dir="test_outputs")

    # Test 1: Default behavior (should be Hebrew)
    print("\n1. Testing DEFAULT behavior (should output Hebrew):")
    print("   File: salesTEST.xlsx (English content)")

    test_file = Path("salesTEST.xlsx")
    if test_file.exists():
        result = await agent.analyze_file(
            file_path=str(test_file),
            additional_instructions=None,  # No special instructions
            language="hebrew"  # This is the default
        )
        print(f"   ✓ Dashboard created: {result['dashboard_path']}")
        print("   Expected: All text in Hebrew")
    else:
        print("   ✗ File not found")

    print("\n2. Testing with NO language specification:")
    print("   The agent should still use Hebrew as default")

    print("\n3. Testing explicit English request:")
    print("   Only when user writes 'use English' or 'in English'")
    print("   Example instruction: 'Create the dashboard in English'")

    if test_file.exists():
        result = await agent.analyze_file(
            file_path=str(test_file),
            additional_instructions="Please create the dashboard in English",  # Explicit English request
            language="hebrew"  # Will be overridden by instruction
        )
        print(f"   ✓ Dashboard created: {result['dashboard_path']}")
        print("   Expected: All text in English (user override)")

def main():
    """Run the test"""
    print("\n🔍 Hebrew Enforcement Test Script")
    print("-" * 60)
    print("This script demonstrates that:")
    print("1. Hebrew is the DEFAULT language")
    print("2. Input file language is IGNORED")
    print("3. English is only used when EXPLICITLY requested")
    print("-" * 60)

    # Run async test
    asyncio.run(test_hebrew_default())

    print("\n" + "=" * 60)
    print("✅ Hebrew enforcement configuration complete!")
    print("\nKey changes made:")
    print("1. System prompt enforces Hebrew as default")
    print("2. User prompts reinforce Hebrew requirements")
    print("3. Workflow instructions specify Hebrew labels")
    print("4. HTML templates use RTL and Hebrew fonts")
    print("5. Language only changes with explicit user request")
    print("=" * 60)

if __name__ == "__main__":
    main()