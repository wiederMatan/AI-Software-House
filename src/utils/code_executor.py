"""Code execution utilities for safe Python code testing."""

import io
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """
    Result of code execution.

    Attributes:
        success: Whether execution completed without errors
        output: Captured stdout output
        error: Error message if execution failed
        namespace: Execution namespace with variables/functions
    """

    success: bool
    output: str
    error: Optional[str] = None
    namespace: Optional[Dict[str, Any]] = None


class CodeExecutor:
    """
    Safe executor for Python code with output capture.

    This class provides isolated execution environment with
    stdout/stderr capture for testing generated code.
    """

    @staticmethod
    def execute(code: str) -> ExecutionResult:
        """
        Execute Python code in a controlled environment.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult with success status, output, and errors
        """
        logger.debug("Executing code in isolated environment")

        # Create isolated namespace
        execution_namespace: Dict[str, Any] = {}
        output = ""
        error = None
        success = False

        # Save original stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            # Redirect stdout to capture output
            sys.stdout = captured_output = io.StringIO()
            sys.stderr = captured_errors = io.StringIO()

            # Execute the code
            exec(code, execution_namespace)

            # Restore stdout/stderr and get output
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            output = captured_output.getvalue()
            error_output = captured_errors.getvalue()

            if error_output:
                logger.warning(f"Stderr output: {error_output}")

            success = True
            logger.debug("Code execution successful")

        except Exception as e:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            error = f"{type(e).__name__}: {str(e)}"
            success = False
            logger.error(f"Code execution failed: {error}")

        return ExecutionResult(
            success=success,
            output=output,
            error=error,
            namespace=execution_namespace if success else None,
        )

    @staticmethod
    def clean_code(code: str) -> str:
        """
        Clean code by removing markdown formatting.

        Args:
            code: Raw code that may contain markdown fences

        Returns:
            Cleaned Python code
        """
        code = code.strip()

        # Remove markdown code fences
        if code.startswith("```python"):
            code = code.split("```python", 1)[1]
        elif code.startswith("```"):
            code = code.split("```", 1)[1]

        if code.endswith("```"):
            code = code.rsplit("```", 1)[0]

        return code.strip()
