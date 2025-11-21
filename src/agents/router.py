"""Router for workflow control flow decisions."""

from typing import Literal

from ..state import AgentState
from ..utils import get_logger

logger = get_logger(__name__)


class Router:
    """
    Router that decides workflow progression.

    Determines whether to continue fixing code or end the workflow
    based on test results and iteration count.
    """

    @staticmethod
    def route(state: AgentState) -> Literal["developer", "end"]:
        """
        Decide next step in workflow based on current state.

        Args:
            state: Current workflow state

        Returns:
            "developer" to continue fixing, "end" to complete workflow
        """
        # Check if tests passed
        if state["status"] == "passed":
            print("\n" + "=" * 80)
            print("🎉 SUCCESS - All tests passed!")
            print("=" * 80)
            logger.info("Workflow completed successfully")
            return "end"

        # Check if max iterations reached
        if state["iteration"] >= state["max_iterations"]:
            print("\n" + "=" * 80)
            print(f"⚠️  STOPPED - Maximum iterations ({state['max_iterations']}) reached")
            print("=" * 80)
            state["status"] = "failed"
            logger.warning("Max iterations reached, stopping workflow")
            return "end"

        # Continue to developer for fixes
        state["iteration"] += 1
        print("\n" + "=" * 80)
        print(f"🔄 Routing back to Developer for iteration {state['iteration']}")
        print("=" * 80)
        logger.info(f"Routing to developer for iteration {state['iteration']}")
        return "developer"
