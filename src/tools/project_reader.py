"""
Project Reader Tool

Provides the read_project_overview function tool for the Agent SDK.
"""

import os
from pathlib import Path
from agents import function_tool


@function_tool
def read_project_overview(project_path: str) -> str:
    """
    Read the project overview file from the specified project directory.

    This tool reads the project_overview.md file which contains comprehensive
    information about the project structure, sample data schemas, scripts,
    and data processing flows.

    Args:
        project_path: Absolute or relative path to the project root directory

    Returns:
        The contents of project_overview.md if found, or an error message
    """
    # Normalize the path
    project_dir = Path(project_path).resolve()

    # Check if directory exists
    if not project_dir.exists():
        return f"Error: Project directory not found: {project_dir}"

    if not project_dir.is_dir():
        return f"Error: Path is not a directory: {project_dir}"

    # Look for project_overview.md
    overview_path = project_dir / "project_overview.md"

    if not overview_path.exists():
        # List available files to help debugging
        available_files = list(project_dir.glob("*"))
        file_list = ", ".join([f.name for f in available_files[:10]])
        return (
            f"Error: project_overview.md not found in {project_dir}\n"
            f"Available files: {file_list}"
        )

    # Read and return the contents
    try:
        with open(overview_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading project_overview.md: {str(e)}"
