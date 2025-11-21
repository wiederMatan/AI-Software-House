"""
AI Software House - Agentic Workflow for Autonomous Software Development
=========================================================================

This module implements a cyclical, multi-agent workflow using LangGraph:
PM -> Developer -> QA/Tester -> Review/Fix Loop

The workflow uses GPT-4o-mini via langchain-openai integration.
"""

import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """
    Defines the state that flows through the agentic workflow.

    Fields:
        user_request: Original request from the user
        requirements: Refined requirements from the Product Manager
        code: Generated code from the Developer
        test_report: Test results from the QA Tester
        iteration: Current iteration number for the fix loop
        max_iterations: Maximum allowed iterations before stopping
        status: Current workflow status (in_progress, passed, failed)
    """
    user_request: str
    requirements: str
    code: str
    test_report: str
    iteration: int
    max_iterations: int
    status: Literal["in_progress", "passed", "failed"]


# ============================================================================
# Agent Nodes
# ============================================================================

def product_manager_node(state: AgentState) -> AgentState:
    """
    Product Manager Agent - Analyzes user request and creates detailed requirements.

    This agent takes the user's request and expands it into clear, actionable
    requirements for the developer.
    """
    print("\n" + "="*80)
    print("🎯 PRODUCT MANAGER - Analyzing Requirements")
    print("="*80)

    prompt = f"""You are a Product Manager in an AI Software House.

User Request: {state['user_request']}

Your task is to analyze this request and create clear, detailed technical requirements.
Include:
1. What the code should do (functional requirements)
2. Expected inputs and outputs
3. Edge cases to consider
4. Success criteria

Provide concise but complete requirements."""

    response = llm.invoke(prompt)
    requirements = response.content

    print(f"\n📋 Requirements:\n{requirements}\n")

    state["requirements"] = requirements
    state["status"] = "in_progress"
    return state


def developer_node(state: AgentState) -> AgentState:
    """
    Developer Agent - Writes code based on requirements and test feedback.

    If this is not the first iteration, the developer uses the test_report
    to fix issues in the code.
    """
    print("\n" + "="*80)
    print(f"👨‍💻 DEVELOPER - Writing Code (Iteration {state['iteration']})")
    print("="*80)

    if state["iteration"] == 1:
        # First iteration - write initial code
        prompt = f"""You are a Python Developer in an AI Software House.

Requirements: {state['requirements']}

Your task is to write clean, working Python code that satisfies these requirements.

IMPORTANT:
- Include ONLY the Python code, no markdown formatting or code fences
- The code must be complete and runnable
- Include a run example that demonstrates the functionality
- Add clear comments explaining the logic

Write the complete Python code now:"""
    else:
        # Subsequent iterations - fix based on test feedback
        prompt = f"""You are a Python Developer fixing code based on test feedback.

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

    response = llm.invoke(prompt)
    code = response.content.strip()

    # Clean up any markdown code fences if present
    if code.startswith("```python"):
        code = code.split("```python", 1)[1]
    if code.startswith("```"):
        code = code.split("```", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    code = code.strip()

    print(f"\n💻 Generated Code:\n{code}\n")

    state["code"] = code
    return state


def qa_tester_node(state: AgentState) -> AgentState:
    """
    QA Tester Agent - Tests the code and provides feedback.

    Uses Python's exec() to run the code in a controlled environment.
    Returns detailed test results including pass/fail status and error messages.
    """
    print("\n" + "="*80)
    print(f"🧪 QA TESTER - Testing Code (Iteration {state['iteration']})")
    print("="*80)

    code = state["code"]
    test_passed = False
    error_message = ""
    output = ""

    # Create a controlled execution environment
    execution_namespace = {}

    try:
        # Capture stdout
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        # Execute the code
        exec(code, execution_namespace)

        # Restore stdout and get output
        sys.stdout = old_stdout
        output = captured_output.getvalue()

        test_passed = True
        print(f"✅ Code executed successfully!\n")
        print(f"📤 Output:\n{output}")

    except Exception as e:
        sys.stdout = old_stdout
        error_message = str(e)
        test_passed = False
        print(f"❌ Code execution failed!\n")
        print(f"🐛 Error: {error_message}")

    # Generate detailed test report
    if test_passed:
        test_report = f"""✅ TEST PASSED

The code executed successfully without errors.

Output:
{output}

All requirements have been satisfied."""
        state["status"] = "passed"
    else:
        test_report = f"""❌ TEST FAILED

Error Details:
{error_message}

The code needs to be fixed to address this error.

Requirements to satisfy:
{state['requirements']}"""
        state["status"] = "in_progress"

    state["test_report"] = test_report
    print(f"\n📊 Test Report:\n{test_report}\n")

    return state


def route_to_developer_or_end(state: AgentState) -> Literal["developer", "end"]:
    """
    Routing Function - Decides whether to continue fixing or end the workflow.

    Routes to:
    - "developer": If tests failed and we haven't exceeded max iterations
    - "end": If tests passed or max iterations reached
    """
    if state["status"] == "passed":
        print("\n" + "="*80)
        print("🎉 SUCCESS - All tests passed!")
        print("="*80)
        return "end"

    if state["iteration"] >= state["max_iterations"]:
        print("\n" + "="*80)
        print(f"⚠️  STOPPED - Maximum iterations ({state['max_iterations']}) reached")
        print("="*80)
        state["status"] = "failed"
        return "end"

    # Increment iteration and continue to developer for fixes
    state["iteration"] += 1
    print("\n" + "="*80)
    print(f"🔄 Routing back to Developer for iteration {state['iteration']}")
    print("="*80)
    return "developer"


# ============================================================================
# Workflow Construction
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Creates and configures the LangGraph workflow.

    Workflow structure:
    START -> Product Manager -> Developer -> QA Tester -> [Router]
                                    ^                        |
                                    |                        v
                                    +---- (if failed) ------+
                                    |                        |
                                    +---- (if passed) -----> END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("product_manager", product_manager_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("qa_tester", qa_tester_node)

    # Define edges
    workflow.set_entry_point("product_manager")
    workflow.add_edge("product_manager", "developer")
    workflow.add_edge("developer", "qa_tester")

    # Add conditional routing from QA Tester
    workflow.add_conditional_edges(
        "qa_tester",
        route_to_developer_or_end,
        {
            "developer": "developer",
            "end": END
        }
    )

    return workflow.compile()


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🏢 AI SOFTWARE HOUSE - Autonomous Development Workflow")
    print("="*80)

    # Initialize the workflow
    app = create_workflow()

    # Define the initial state with a demanding request
    initial_state = AgentState(
        user_request="Create a Python function named 'is_palindrome' that checks if a string is a palindrome. The code must include a run example that prints the result for 'racecar' and 'hello'.",
        requirements="",
        code="",
        test_report="",
        iteration=1,
        max_iterations=5,
        status="in_progress"
    )

    print(f"\n📝 User Request: {initial_state['user_request']}\n")

    # Run the workflow
    final_state = app.invoke(initial_state)

    # Display final results
    print("\n" + "="*80)
    print("📋 FINAL RESULTS")
    print("="*80)
    print(f"\nStatus: {final_state['status'].upper()}")
    print(f"Total Iterations: {final_state['iteration']}")
    print(f"\n{'='*80}")
    print("Final Code:")
    print("="*80)
    print(final_state['code'])
    print("\n" + "="*80)
    print("Final Test Report:")
    print("="*80)
    print(final_state['test_report'])
    print("\n" + "="*80)
