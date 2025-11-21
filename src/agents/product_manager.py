"""Product Manager agent for requirements analysis."""

from langchain_openai import ChatOpenAI

from .base_agent import BaseAgent
from ..state import AgentState


class ProductManagerAgent(BaseAgent):
    """
    Product Manager agent that analyzes user requests and creates requirements.

    This agent takes the user's request and expands it into clear,
    actionable technical requirements for the developer.
    """

    def __init__(self, llm: ChatOpenAI):
        """
        Initialize the Product Manager agent.

        Args:
            llm: Language model instance
        """
        super().__init__(llm)

    def process(self, state: AgentState) -> AgentState:
        """
        Analyze user request and create detailed requirements.

        Args:
            state: Current workflow state

        Returns:
            Updated state with requirements field populated
        """
        self._log_section("🎯 PRODUCT MANAGER - Analyzing Requirements")
        self.logger.info("Analyzing user request")

        prompt = self._create_prompt(state["user_request"])
        response = self.llm.invoke(prompt)
        requirements = response.content

        print(f"\n📋 Requirements:\n{requirements}\n")
        self.logger.info("Requirements analysis complete")

        state["requirements"] = requirements
        state["status"] = "in_progress"

        return state

    def _create_prompt(self, user_request: str) -> str:
        """
        Create the prompt for requirements analysis.

        Args:
            user_request: User's original request

        Returns:
            Formatted prompt for the LLM
        """
        return f"""You are a Product Manager in an AI Software House.

User Request: {user_request}

Your task is to analyze this request and create clear, detailed technical requirements.
Include:
1. What the code should do (functional requirements)
2. Expected inputs and outputs
3. Edge cases to consider
4. Success criteria

Provide concise but complete requirements."""
