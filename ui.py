#!/usr/bin/env python3
"""
AI Software House - Streamlit Web UI

A user-friendly web interface for the AI Software House autonomous development system.
"""

import streamlit as st
from typing import Optional
import sys
from io import StringIO

from src.config import Settings
from src.workflow import WorkflowBuilder
from src.utils import setup_logging


# Page configuration
st.set_page_config(
    page_title="AI Software House",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #764ba2;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .code-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'workflow_executed' not in st.session_state:
        st.session_state.workflow_executed = False
    if 'final_state' not in st.session_state:
        st.session_state.final_state = None
    if 'workflow_output' not in st.session_state:
        st.session_state.workflow_output = ""


def capture_workflow_output(user_request: str, settings: Settings) -> tuple:
    """
    Execute workflow and capture all output.

    Args:
        user_request: User's code generation request
        settings: Application settings

    Returns:
        Tuple of (final_state, captured_output)
    """
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        # Setup logging to captured output
        setup_logging(settings.log_level)

        # Build and run workflow
        builder = WorkflowBuilder(settings)
        workflow = builder.build()
        initial_state = builder.create_initial_state(user_request)

        # Execute workflow
        final_state = workflow.invoke(initial_state)

        # Restore stdout
        sys.stdout = old_stdout
        output = captured_output.getvalue()

        return final_state, output

    except Exception as e:
        sys.stdout = old_stdout
        raise e


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Model settings
        st.subheader("Model Settings")
        model_name = st.selectbox(
            "LLM Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="Select the OpenAI model to use"
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative, lower values more deterministic"
        )

        # Workflow settings
        st.subheader("Workflow Settings")
        max_iterations = st.number_input(
            "Max Iterations",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum number of fix attempts before giving up"
        )

        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1,
            help="Logging verbosity level"
        )

        st.divider()

        # Examples
        st.subheader("📝 Example Requests")
        examples = {
            "Palindrome Checker": "Create a Python function named 'is_palindrome' that checks if a string is a palindrome. Include run examples.",
            "Fibonacci Sequence": "Create a function that generates the first n numbers in the Fibonacci sequence. Include examples for n=10.",
            "Prime Number Checker": "Create a function that checks if a number is prime. Include tests for 2, 17, and 100.",
            "String Reverser": "Create a function that reverses a string without using built-in reverse methods.",
            "List Deduplicator": "Create a function that removes duplicates from a list while preserving order.",
        }

        selected_example = st.selectbox(
            "Load Example",
            [""] + list(examples.keys()),
            help="Select an example to load into the request field"
        )

        if selected_example and st.button("Load Example"):
            st.session_state.example_request = examples[selected_example]

        st.divider()

        # About
        st.subheader("ℹ️ About")
        st.markdown("""
        **AI Software House** is an autonomous software development system that:

        - 🎯 Analyzes requirements
        - 👨‍💻 Writes code
        - 🧪 Tests automatically
        - 🔄 Self-corrects errors

        Built with LangGraph and GPT-4o-mini.
        """)

        return {
            "model_name": model_name,
            "temperature": temperature,
            "max_iterations": max_iterations,
            "log_level": log_level,
        }


def render_main_content(config: dict):
    """
    Render the main content area.

    Args:
        config: Configuration dictionary from sidebar
    """
    # Header
    st.markdown('<h1 class="main-header">🏢 AI Software House</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">'
        'Autonomous Code Generation with Multi-Agent Workflow'
        '</p>',
        unsafe_allow_html=True
    )

    # Request input
    st.subheader("📝 What do you want to build?")

    # Check if we have an example to load
    default_request = st.session_state.get('example_request', "")
    if default_request:
        user_request = st.text_area(
            "Describe your code requirements:",
            value=default_request,
            height=120,
            placeholder="Example: Create a Python function that...",
            help="Describe what you want the AI to build"
        )
        # Clear the example from session state
        if 'example_request' in st.session_state:
            del st.session_state.example_request
    else:
        user_request = st.text_area(
            "Describe your code requirements:",
            height=120,
            placeholder="Example: Create a Python function that...",
            help="Describe what you want the AI to build"
        )

    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate Code", type="primary")

    # Execute workflow
    if generate_button and user_request:
        st.session_state.workflow_executed = False

        with st.spinner("🤖 AI agents are working on your request..."):
            try:
                # Create settings from config
                settings = Settings(
                    openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
                    model_name=config["model_name"],
                    temperature=config["temperature"],
                    max_iterations=config["max_iterations"],
                    log_level=config["log_level"],
                )

                # Validate settings
                settings.validate()

                # Execute workflow
                final_state, output = capture_workflow_output(user_request, settings)

                # Store in session state
                st.session_state.final_state = final_state
                st.session_state.workflow_output = output
                st.session_state.workflow_executed = True

            except ValueError as e:
                st.error(f"❌ Configuration Error: {str(e)}")
                st.info("💡 Make sure to set your OPENAI_API_KEY in Streamlit secrets")
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")

    # Display results
    if st.session_state.workflow_executed and st.session_state.final_state:
        display_results(st.session_state.final_state, st.session_state.workflow_output)


def display_results(final_state: dict, workflow_output: str):
    """
    Display workflow results in a nice format.

    Args:
        final_state: Final workflow state
        workflow_output: Captured console output
    """
    st.divider()

    # Status banner
    status = final_state["status"]
    iterations = final_state["iteration"]

    if status == "passed":
        st.markdown(
            f'<div class="success-box">'
            f'<h3>✅ Success! Code generated and tested in {iterations} iteration(s)</h3>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="error-box">'
            f'<h3>⚠️ Maximum iterations reached ({iterations})</h3>'
            f'<p>The code may not be fully working. Review the test report below.</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Generated Code",
        "📊 Test Report",
        "📋 Requirements",
        "🔍 Workflow Log"
    ])

    with tab1:
        st.subheader("Generated Code")
        st.code(final_state["code"], language="python")

        # Download button
        st.download_button(
            label="⬇️ Download Code",
            data=final_state["code"],
            file_name="generated_code.py",
            mime="text/x-python",
        )

    with tab2:
        st.subheader("Test Report")
        if status == "passed":
            st.success("All tests passed! ✅")
        else:
            st.warning("Tests did not pass completely")

        st.text(final_state["test_report"])

    with tab3:
        st.subheader("Requirements Analysis")
        st.markdown(final_state["requirements"])

    with tab4:
        st.subheader("Workflow Execution Log")
        st.text(workflow_output)

        # Show metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Iterations", iterations)
        with col2:
            st.metric("Status", status.upper())
        with col3:
            st.metric("Code Lines", len(final_state["code"].split("\n")))


def main():
    """Main application entry point."""
    initialize_session_state()

    # Render UI
    config = render_sidebar()
    render_main_content(config)

    # Footer
    st.divider()
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Built with ❤️ using LangGraph, LangChain, and Streamlit | '
        '<a href="https://github.com" target="_blank">View on GitHub</a>'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
