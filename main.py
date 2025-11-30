"""
Project Structure Analyzer - Main Entry Point

This agent system analyzes GitHub projects to understand their structure
and identify differences between sample data and production data.
"""

import asyncio
import sys
from pathlib import Path

from src.agent import analyze_project, create_project_analyzer
from agents import Runner


async def main():
    """Main entry point for the project analyzer."""

    print("=" * 60)
    print("Project Structure Analyzer - Step 2")
    print("=" * 60)
    print()

    # Default to the sample project for testing
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Use the test sample project
        project_path = str(Path(__file__).parent / "tests" / "sample_project")

    print(f"Analyzing project: {project_path}")
    print("-" * 60)
    print()

    try:
        result = await analyze_project(project_path)
        print("Agent's Analysis:")
        print("-" * 60)
        print(result)
        print()
        print("=" * 60)
        print("Analysis complete.")

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


def run_sync():
    """Synchronous wrapper for main."""
    asyncio.run(main())


if __name__ == "__main__":
    run_sync()
