"""State definition for the agentic workflow."""

from typing import TypedDict, Literal
from enum import Enum


class WorkflowStatus(str, Enum):
    """Enumeration of possible workflow statuses."""

    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"


class AgentState(TypedDict):
    """
    State that flows through the agentic workflow.

    This state is passed between all agents and tracks the complete
    context of the software development process.

    Attributes:
        user_request: Original request from the user
        requirements: Refined requirements from the Product Manager
        code: Generated code from the Developer
        test_report: Test results from the QA Tester
        iteration: Current iteration number for the fix loop
        max_iterations: Maximum allowed iterations before stopping
        status: Current workflow status
    """

    user_request: str
    requirements: str
    code: str
    test_report: str
    iteration: int
    max_iterations: int
    status: Literal["in_progress", "passed", "failed"]
