"""LangGraph workflow builder for the AI Software House."""

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from ..state import AgentState
from ..agents import (
    ProductManagerAgent,
    DeveloperAgent,
    QATesterAgent,
    Router,
)
from ..config import Settings
from ..utils import get_logger

logger = get_logger(__name__)


class WorkflowBuilder:
    """
    Builder class for constructing the LangGraph workflow.

    This class creates and configures the complete workflow graph
    with all agents and routing logic.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the workflow builder.

        Args:
            settings: Application settings and configuration
        """
        self.settings = settings
        self.llm = self._create_llm()
        self.router = Router()

    def _create_llm(self) -> ChatOpenAI:
        """
        Create the LLM instance with configured settings.

        Returns:
            Configured ChatOpenAI instance
        """
        logger.info(
            f"Initializing LLM: {self.settings.model_name} "
            f"(temperature={self.settings.temperature})"
        )

        return ChatOpenAI(
            model=self.settings.model_name,
            temperature=self.settings.temperature,
            api_key=self.settings.openai_api_key,
        )

    def build(self) -> StateGraph:
        """
        Build and compile the complete workflow graph.

        Returns:
            Compiled StateGraph ready for execution

        The workflow structure:
            START → PM → Developer → QA → [Router]
                           ↑              |
                           |              ↓
                           +--- (fail) --+
                           |              |
                           +--- (pass) → END
        """
        logger.info("Building workflow graph")

        # Initialize agents
        pm_agent = ProductManagerAgent(self.llm)
        dev_agent = DeveloperAgent(self.llm)
        qa_agent = QATesterAgent()

        # Create workflow graph
        workflow = StateGraph(AgentState)

        # Add agent nodes
        workflow.add_node("product_manager", pm_agent.process)
        workflow.add_node("developer", dev_agent.process)
        workflow.add_node("qa_tester", qa_agent.process)

        # Define workflow edges
        workflow.set_entry_point("product_manager")
        workflow.add_edge("product_manager", "developer")
        workflow.add_edge("developer", "qa_tester")

        # Add conditional routing from QA Tester
        workflow.add_conditional_edges(
            "qa_tester",
            self.router.route,
            {"developer": "developer", "end": END},
        )

        logger.info("Workflow graph built successfully")
        return workflow.compile()

    def create_initial_state(self, user_request: str) -> AgentState:
        """
        Create initial state for workflow execution.

        Args:
            user_request: User's request for code generation

        Returns:
            Initial AgentState ready for workflow execution
        """
        return AgentState(
            user_request=user_request,
            requirements="",
            code="",
            test_report="",
            iteration=1,
            max_iterations=self.settings.max_iterations,
            status="in_progress",
        )
