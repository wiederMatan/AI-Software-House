"""Base agent class for all workflow agents."""

from abc import ABC, abstractmethod
from typing import Optional
from langchain_openai import ChatOpenAI

from ..state import AgentState
from ..utils import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the workflow.

    All agents must implement the process() method that takes
    an AgentState and returns an updated AgentState.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize the base agent.

        Args:
            llm: Language model instance (optional, can be injected)
        """
        self.llm = llm
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and return updated state.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        pass

    def _log_section(self, title: str, width: int = 80) -> None:
        """
        Log a formatted section header.

        Args:
            title: Section title
            width: Width of the section separator
        """
        separator = "=" * width
        print(f"\n{separator}")
        print(title)
        print(separator)
