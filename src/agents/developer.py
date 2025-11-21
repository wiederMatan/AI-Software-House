"""Developer agent for code generation and fixes."""

from langchain_openai import ChatOpenAI

from .base_agent import BaseAgent
from ..state import AgentState
from ..utils import CodeExecutor


class DeveloperAgent(BaseAgent):
    """
    Developer agent that writes code based on requirements and test feedback.

    On first iteration: Writes initial code based on requirements
    On subsequent iterations: Fixes code based on test feedback
    """

    def __init__(self, llm: ChatOpenAI):
        """
        Initialize the Developer agent.

        Args:
            llm: Language model instance
        """
        super().__init__(llm)

    def process(self, state: AgentState) -> AgentState:
        """
        Write or fix code based on current iteration.

        Args:
            state: Current workflow state

        Returns:
            Updated state with code field populated
        """
        iteration = state["iteration"]
        self._log_section(f"👨‍💻 DEVELOPER - Writing Code (Iteration {iteration})")
        self.logger.info(f"Starting code generation (iteration {iteration})")

        # Determine if this is initial code or a fix
        is_initial = iteration == 1
        prompt = (
            self._create_initial_prompt(state["requirements"])
            if is_initial
            else self._create_fix_prompt(state)
        )

        # Generate code
        response = self.llm.invoke(prompt)
        code = CodeExecutor.clean_code(response.content)

        print(f"\n💻 Generated Code:\n{code}\n")
        self.logger.info("Code generation complete")

        state["code"] = code
        return state

    def _create_initial_prompt(self, requirements: str) -> str:
        """
        Create prompt for initial code generation.

        Args:
            requirements: Technical requirements from PM

        Returns:
            Formatted prompt for the LLM
        """
        return f"""You are a Python Developer in an AI Software House.

Requirements: {requirements}

Your task is to write clean, working Python code that satisfies these requirements.

IMPORTANT:
- Include ONLY the Python code, no markdown formatting or code fences
- The code must be complete and runnable
- Include a run example that demonstrates the functionality
- Add clear comments explaining the logic

Write the complete Python code now:"""

    def _create_fix_prompt(self, state: AgentState) -> str:
        """
        Create prompt for fixing code based on test feedback.

        Args:
            state: Current workflow state with previous code and test results

        Returns:
            Formatted prompt for the LLM
        """
        return f"""You are a Python Developer fixing code based on test feedback.

Original Requirements: {state['requirements']}

Previous Code:
{state['code']}

Test Report:
{state['test_report']}

Your task is to fix the code based on the test feedback.

IMPORTANT:
- Include ONLY the Python code, no markdown formatting or code fences
- Fix all issues mentioned in the test report
- The code must be complete and runnable
- Include the run example

Write the fixed Python code now:"""
