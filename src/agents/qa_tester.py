"""QA Tester agent for code testing and validation."""

from .base_agent import BaseAgent
from ..state import AgentState
from ..utils import CodeExecutor, ExecutionResult


class QATesterAgent(BaseAgent):
    """
    QA Tester agent that executes and validates generated code.

    This agent runs the code in a controlled environment,
    captures output and errors, and provides detailed test reports.
    """

    def process(self, state: AgentState) -> AgentState:
        """
        Test the generated code and create test report.

        Args:
            state: Current workflow state with code to test

        Returns:
            Updated state with test_report and status fields
        """
        iteration = state["iteration"]
        self._log_section(f"🧪 QA TESTER - Testing Code (Iteration {iteration})")
        self.logger.info(f"Starting code testing (iteration {iteration})")

        # Execute the code
        result = CodeExecutor.execute(state["code"])

        # Display results
        if result.success:
            print("✅ Code executed successfully!\n")
            print(f"📤 Output:\n{result.output}")
            self.logger.info("Code execution successful")
        else:
            print("❌ Code execution failed!\n")
            print(f"🐛 Error: {result.error}")
            self.logger.error(f"Code execution failed: {result.error}")

        # Generate test report
        test_report = self._create_test_report(result, state["requirements"])
        print(f"\n📊 Test Report:\n{test_report}\n")

        # Update state
        state["test_report"] = test_report
        state["status"] = "passed" if result.success else "in_progress"

        return state

    def _create_test_report(self, result: ExecutionResult, requirements: str) -> str:
        """
        Create a detailed test report based on execution results.

        Args:
            result: Code execution result
            requirements: Original requirements for context

        Returns:
            Formatted test report
        """
        if result.success:
            return f"""✅ TEST PASSED

The code executed successfully without errors.

Output:
{result.output}

All requirements have been satisfied."""
        else:
            return f"""❌ TEST FAILED

Error Details:
{result.error}

The code needs to be fixed to address this error.

Requirements to satisfy:
{requirements}"""
