# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Software House is an autonomous software development system that implements a cyclical, multi-agent workflow using LangGraph and GPT-4o-mini. The system mimics a complete software development team with coordinated agents working together to generate tested, working code.

**Core Workflow**: Product Manager → Developer → QA Tester → Review/Fix Loop

## Architecture

The codebase follows a **modular architecture** with clear separation of concerns:

### Module Structure

```
src/
├── agents/          # Individual agent implementations
├── config/          # Configuration and settings management
├── state/           # State definitions and management
├── utils/           # Reusable utilities (logging, code execution)
└── workflow/        # Workflow orchestration with LangGraph
```

### State Management

Located in `src/state/agent_state.py`:

The system uses LangGraph's `StateGraph` with a TypedDict called `AgentState` containing:
- `user_request`: Original request from user
- `requirements`: Refined requirements from PM
- `code`: Generated Python code
- `test_report`: Test results from QA
- `iteration`: Current iteration number
- `max_iterations`: Max allowed iterations (default: 5)
- `status`: Workflow status ("in_progress", "passed", "failed")

### Agent Implementations

All agents inherit from `BaseAgent` (src/agents/base_agent.py) which provides:
- Abstract `process(state) -> state` method
- Logging infrastructure
- Common formatting utilities

1. **ProductManagerAgent** - src/agents/product_manager.py
   - Analyzes user requests and creates detailed technical requirements
   - Defines success criteria, inputs/outputs, and edge cases
   - Entry point for the workflow

2. **DeveloperAgent** - src/agents/developer.py
   - Writes Python code based on requirements (iteration 1)
   - Fixes code based on test feedback (iterations 2+)
   - Uses `test_report` field for self-correction
   - Cleans LLM output using `CodeExecutor.clean_code()`

3. **QATesterAgent** - src/agents/qa_tester.py
   - Executes code using `CodeExecutor` utility
   - Captures stdout and errors in isolated environment
   - Generates detailed test reports
   - Updates status to "passed" or keeps as "in_progress"

4. **Router** - src/agents/router.py
   - Static routing logic (no LLM needed)
   - Routes to "developer" if tests failed and iterations remain
   - Routes to "end" if tests passed or max iterations reached
   - Manages iteration counter

### Workflow Graph Structure

```
START → product_manager → developer → qa_tester → [router]
                              ↑                       |
                              |                       ↓
                              +----- (if failed) ----+
                              |                       |
                              +----- (if passed) --> END
```

## Development Commands

### Run the workflow
```bash
source venv/bin/activate

# Recommended: Use modular entry point
python main.py

# Legacy: Use monolithic script
python software_house.py
```

### Install dependencies
```bash
pip install -r requirements.txt
# or manually:
pip install langchain langchain-openai langgraph openai python-dotenv
```

### Environment setup
Ensure `.env` contains (see `.env.example`):
```bash
# Required
OPENAI_API_KEY=your-key-here

# Optional (with defaults shown)
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.7
MAX_ITERATIONS=5
LOG_LEVEL=INFO
```

## Key Implementation Details

### Configuration Management (src/config/settings.py)
- Environment-based configuration using `python-dotenv`
- `Settings.from_env()` loads and validates all settings
- Validation ensures temperature (0.0-1.0), max_iterations (≥1), and valid log levels

### Code Execution Safety (src/utils/code_executor.py)
The `CodeExecutor` class provides:
- Isolated namespace execution
- Stdout/stderr capture
- Exception handling with detailed error messages
- `ExecutionResult` dataclass with success status, output, and errors

```python
result = CodeExecutor.execute(code)
# Returns: ExecutionResult(success=bool, output=str, error=str|None)
```

### Logging Infrastructure (src/utils/logger.py)
- Centralized logging setup
- Configurable log levels via environment
- Per-module loggers via `get_logger(__name__)`
- Formatted output with timestamps

### LLM Configuration (src/workflow/graph_builder.py)
- Model configured via `Settings` class
- Single LLM instance shared across agents
- Default: `gpt-4o-mini` with temperature 0.7

### Code Cleaning (src/utils/code_executor.py)
`CodeExecutor.clean_code()` strips markdown fences from LLM output:
- Removes ```python and ``` wrappers
- Ensures clean, executable Python code

### Self-Correction Loop
Failed tests trigger re-routing to developer with detailed error messages. The developer's prompt changes from `_create_initial_prompt()` to `_create_fix_prompt()` which includes the test report.

## Modifying the Workflow

### Change the user request
Edit `user_request` variable in `main.py` (line ~96)

### Adjust configuration
Add/modify environment variables in `.env`:
```bash
MAX_ITERATIONS=10       # Change max fix attempts
MODEL_NAME=gpt-4        # Use different model
TEMPERATURE=0.3         # More deterministic
LOG_LEVEL=DEBUG         # More verbose logging
```

### Add new agents
1. Create new agent class in `src/agents/` inheriting from `BaseAgent`
2. Implement `process(state: AgentState) -> AgentState` method
3. Register in `src/workflow/graph_builder.py`:
   ```python
   new_agent = NewAgent(self.llm)
   workflow.add_node("new_agent", new_agent.process)
   workflow.add_edge("previous_node", "new_agent")
   ```

### Extend AgentState
1. Modify `src/state/agent_state.py` to add new fields
2. Update agents to populate/consume new fields
3. No changes needed to workflow graph (state is passed through)

## File Structure

### Core Files
- `main.py` - Main entry point (recommended)
- `software_house.py` - Legacy monolithic script (kept for backward compatibility)
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not in git)
- `.env.example` - Template for environment setup

### Source Modules (src/)
- `agents/base_agent.py` - Abstract base class for all agents
- `agents/product_manager.py` - PM agent (~50 lines)
- `agents/developer.py` - Developer agent (~80 lines)
- `agents/qa_tester.py` - QA agent (~60 lines)
- `agents/router.py` - Routing logic (~40 lines)
- `config/settings.py` - Configuration management (~60 lines)
- `state/agent_state.py` - State definition (~30 lines)
- `utils/logger.py` - Logging utilities (~40 lines)
- `utils/code_executor.py` - Code execution (~90 lines)
- `workflow/graph_builder.py` - Workflow builder (~100 lines)

## Important Notes

### Workflow Behavior
- The workflow is synchronous; each agent waits for the previous to complete
- State is immutable between nodes; each node returns updated state
- Workflow terminates on success OR when max_iterations is reached
- All agent outputs are printed to console for transparency

### Code Execution
- Code runs in isolated namespace to prevent pollution
- Stdout/stderr are captured and restored
- Exceptions are caught and reported, never crash the workflow

### Design Patterns
- **Single Responsibility**: Each agent has one clear purpose
- **Dependency Injection**: LLM injected into agents via constructor
- **Configuration as Code**: Settings loaded from environment
- **Type Safety**: Full type hints using TypedDict and dataclasses
- **Logging**: Structured logging throughout for observability

### Best Practices
- Use `main.py` for new features (modular architecture)
- Keep `software_house.py` for backward compatibility only
- Add new configuration via `Settings` class, not hardcoded values
- New agents should inherit from `BaseAgent`
- Test utilities independently (CodeExecutor, logger)
