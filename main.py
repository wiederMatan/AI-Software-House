#!/usr/bin/env python3
"""
AI Software House - Main Entry Point

This is the main entry point for running the AI Software House
autonomous development workflow.
"""

import sys
from typing import Optional

from src.config import Settings
from src.workflow import WorkflowBuilder
from src.utils import setup_logging, get_logger


def print_banner() -> None:
    """Print the application banner."""
    print("\n" + "=" * 80)
    print("🏢 AI SOFTWARE HOUSE - Autonomous Development Workflow")
    print("=" * 80)


def print_final_results(state: dict) -> None:
    """
    Print final workflow results.

    Args:
        state: Final workflow state
    """
    print("\n" + "=" * 80)
    print("📋 FINAL RESULTS")
    print("=" * 80)
    print(f"\nStatus: {state['status'].upper()}")
    print(f"Total Iterations: {state['iteration']}")
    print(f"\n{'=' * 80}")
    print("Final Code:")
    print("=" * 80)
    print(state["code"])
    print("\n" + "=" * 80)
    print("Final Test Report:")
    print("=" * 80)
    print(state["test_report"])
    print("\n" + "=" * 80)


def run_workflow(user_request: str, settings: Optional[Settings] = None) -> dict:
    """
    Run the complete AI Software House workflow.

    Args:
        user_request: User's request for code generation
        settings: Optional settings (uses defaults from env if not provided)

    Returns:
        Final workflow state

    Raises:
        ValueError: If settings are invalid
    """
    # Load settings
    if settings is None:
        settings = Settings.from_env()

    settings.validate()

    # Setup logging
    setup_logging(settings.log_level)
    logger = get_logger(__name__)

    logger.info("Starting AI Software House workflow")
    logger.info(f"User request: {user_request}")

    # Print banner
    print_banner()
    print(f"\n📝 User Request: {user_request}\n")

    # Build workflow
    builder = WorkflowBuilder(settings)
    workflow = builder.build()
    initial_state = builder.create_initial_state(user_request)

    # Execute workflow
    logger.info("Executing workflow")
    final_state = workflow.invoke(initial_state)

    # Display results
    print_final_results(final_state)

    logger.info(f"Workflow completed with status: {final_state['status']}")
    return final_state


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Default request (can be modified or passed as CLI argument)
        user_request = (
            "Create a Python function named 'is_palindrome' that checks if a "
            "string is a palindrome. The code must include a run example that "
            "prints the result for 'racecar' and 'hello'."
        )

        # Run workflow
        final_state = run_workflow(user_request)

        # Return exit code based on workflow status
        return 0 if final_state["status"] == "passed" else 1

    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Unexpected Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
