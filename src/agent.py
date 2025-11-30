"""
Project Analyzer Agent

Defines the agent that analyzes project structures using the read_project_overview tool.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from agents import Agent, Runner
from openai import OpenAI, AzureOpenAI

from src.tools.project_reader import read_project_overview

# Load environment variables
load_dotenv()


def create_openai_client() -> OpenAI:
    """
    Create an OpenAI client.

    Returns:
        Configured OpenAI client
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return OpenAI(api_key=api_key)


def create_azure_client() -> AzureOpenAI:
    """
    Create an Azure OpenAI client.

    Returns:
        Configured Azure OpenAI client
    """
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    if not api_key or not endpoint:
        raise ValueError(
            "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set"
        )

    return AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )


def create_project_analyzer(use_azure: bool = False, model: str = "gpt-4o") -> Agent:
    """
    Create a project analyzer agent.

    Args:
        use_azure: If True, use Azure OpenAI. If False, use OpenAI.
        model: Model name or deployment name to use

    Returns:
        Configured Agent instance
    """
    instructions = """You are a project analyzer assistant. Your role is to understand
the structure and contents of software projects by reading their project overview files.

When asked to analyze a project:
1. Use the read_project_overview tool to read the project's overview file
2. Parse and understand the project structure, including:
   - Project purpose and goals
   - Sample data files and their schemas
   - Scripts and their roles
   - Data processing flows
   - Dependencies and assumptions
3. Provide a clear summary of what you learned about the project

If the project overview file is not found, explain the error and suggest creating one.

Always be specific about data schemas, including column names, data types, and formats."""

    # For now, use default OpenAI configuration
    # Azure support will be added in a future step
    agent = Agent(
        name="Project Analyzer",
        instructions=instructions,
        tools=[read_project_overview],
        model=model
    )

    return agent


async def analyze_project(project_path: str, use_azure: bool = False) -> str:
    """
    Analyze a project and return the agent's understanding.

    Args:
        project_path: Path to the project directory
        use_azure: If True, use Azure OpenAI

    Returns:
        Agent's analysis of the project
    """
    agent = create_project_analyzer(use_azure=use_azure)

    prompt = f"""Please analyze the project located at: {project_path}

Read the project overview file and provide:
1. A summary of what this project does
2. The sample data files and their complete schema information
3. The scripts and what each one does
4. How data flows through the project

Be thorough and specific about the data schema details."""

    result = await Runner.run(agent, prompt)
    return result.final_output
