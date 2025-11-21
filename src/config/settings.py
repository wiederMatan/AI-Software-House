"""Configuration settings for the AI Software House."""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """
    Application settings and configuration.

    Attributes:
        openai_api_key: OpenAI API key from environment
        model_name: LLM model to use (default: gpt-4o-mini)
        temperature: Model temperature for creativity (0.0-1.0)
        max_iterations: Maximum fix iterations before stopping
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_iterations: int = 5
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create Settings instance from environment variables.

        Returns:
            Settings instance with values from environment

        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file."
            )

        return cls(
            openai_api_key=api_key,
            model_name=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "5")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """
        Validate settings values.

        Raises:
            ValueError: If any setting is invalid
        """
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
