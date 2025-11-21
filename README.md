# 🏢 AI Software House

An autonomous software development system powered by **LangGraph** and **GPT-4o-mini**. This project implements a cyclical, multi-agent workflow that mimics a complete software development team:

**Product Manager → Developer → QA Tester → Review/Fix Loop**

## 🌟 Features

- **Multi-Agent Workflow**: Coordinated agents working together to deliver working code
- **Autonomous Development**: From requirements to tested code with minimal human intervention
- **Self-Correcting Loop**: QA feedback drives iterative improvements until tests pass
- **LangGraph State Management**: Robust state tracking across the entire workflow
- **Comprehensive Logging**: Detailed visibility into each agent's actions and decisions
- **🎨 Web UI**: User-friendly Streamlit interface for non-technical users
- **⚙️ Flexible Configuration**: Customize models, temperature, and iteration limits

## 🏗️ Architecture

The system uses a cyclical workflow:

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Product Manager │ - Analyzes request and creates detailed requirements
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Developer     │ - Writes code based on requirements/feedback
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   QA Tester     │ - Tests code using exec() in controlled environment
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Router │
    └───┬─┬──┘
        │ │
  Pass  │ │  Fail
    ┌───┘ └───┐
    │         │
    ▼         ▼
  END    Back to Developer
          (with test feedback)
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## 🚀 Installation

### 1. Clone or navigate to the repository

```bash
cd ai-software-house
```

### 2. Create and activate a virtual environment (if not already done)

```bash
# The venv already exists, so just activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install required dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

**For CLI usage:**

Copy the `.env.example` file to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your-openai-api-key-here` with your actual API key:

```
OPENAI_API_KEY=sk-proj-...
```

**For Web UI usage:**

Copy the Streamlit secrets template:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml` and add your API key:

```toml
OPENAI_API_KEY = "sk-proj-..."
```

## 🎮 Usage

### Option 1: Web UI (Recommended for End-Users) 🌐

Launch the interactive web interface:

```bash
streamlit run ui.py
```

This will open a browser window with a user-friendly interface where you can:
- ✍️ Enter your code requirements in natural language
- ⚙️ Configure model settings (temperature, max iterations)
- 📊 View real-time progress
- 📄 See generated code with syntax highlighting
- 📥 Download the final code
- 🔍 Review test reports and workflow logs

**Perfect for**: Non-technical users, quick prototyping, demonstrations

### Option 2: Command Line Interface

Run the autonomous software development workflow directly:

```bash
# Using the new modular entry point (recommended)
python main.py

# Or using the legacy monolithic script
python software_house.py
```

**Perfect for**: Developers, automation, CI/CD integration

### Default Example

The default run creates a palindrome checker function:

```
User Request: Create a Python function named 'is_palindrome' that checks
if a string is a palindrome. The code must include a run example that
prints the result for 'racecar' and 'hello'.
```

### Customizing the Request

Edit the `user_request` variable in `main.py` (line ~96):

```python
user_request = "Your custom request here"
```

### Advanced Configuration

Configure via environment variables in `.env`:

```bash
# Model configuration
MODEL_NAME=gpt-4o-mini      # LLM model to use
TEMPERATURE=0.7              # Creativity level (0.0-1.0)

# Workflow configuration
MAX_ITERATIONS=5             # Max fix attempts

# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

## 📊 Example Output

```
================================================================================
🏢 AI SOFTWARE HOUSE - Autonomous Development Workflow
================================================================================

📝 User Request: Create a Python function named 'is_palindrome'...

================================================================================
🎯 PRODUCT MANAGER - Analyzing Requirements
================================================================================

📋 Requirements:
[Detailed requirements generated by PM agent...]

================================================================================
👨‍💻 DEVELOPER - Writing Code (Iteration 1)
================================================================================

💻 Generated Code:
[Python code generated by developer agent...]

================================================================================
🧪 QA TESTER - Testing Code (Iteration 1)
================================================================================

✅ Code executed successfully!

📤 Output:
True
False

================================================================================
🎉 SUCCESS - All tests passed!
================================================================================
```

## 🔧 Configuration

The project uses environment-based configuration. Add these to your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-proj-...

# Optional (with defaults)
MODEL_NAME=gpt-4o-mini      # LLM model: gpt-4, gpt-4o-mini, gpt-3.5-turbo
TEMPERATURE=0.7              # Creativity: 0.0 (deterministic) to 1.0 (creative)
MAX_ITERATIONS=5             # Maximum fix attempts before giving up
LOG_LEVEL=INFO              # Logging: DEBUG, INFO, WARNING, ERROR
```

## 📁 Project Structure

```
ai-software-house/
├── src/                         # Source code (modular architecture)
│   ├── agents/                  # Agent implementations
│   │   ├── base_agent.py       # Abstract base agent class
│   │   ├── product_manager.py  # PM agent for requirements
│   │   ├── developer.py        # Developer agent for code generation
│   │   ├── qa_tester.py        # QA agent for testing
│   │   └── router.py           # Routing logic
│   ├── config/                  # Configuration management
│   │   └── settings.py         # Settings with env var support
│   ├── state/                   # State management
│   │   └── agent_state.py      # AgentState TypedDict
│   ├── utils/                   # Utility modules
│   │   ├── logger.py           # Logging utilities
│   │   └── code_executor.py    # Safe code execution
│   └── workflow/                # Workflow orchestration
│       └── graph_builder.py    # LangGraph workflow builder
├── main.py                      # Main entry point (recommended)
├── software_house.py            # Legacy monolithic script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .env.example                 # Template for environment setup
├── README.md                    # This file
└── CLAUDE.md                    # Claude Code guidance
```

### Code Organization

- **Separation of Concerns**: Each agent is in its own module
- **Configuration Management**: Centralized settings with validation
- **Reusable Utilities**: Logger and code executor can be used independently
- **Type Safety**: Full type hints throughout the codebase
- **Extensibility**: Easy to add new agents or modify workflow

## 🛠️ Agents Overview

### 🎯 Product Manager Agent
- Analyzes user requests
- Creates detailed technical requirements
- Defines success criteria and edge cases

### 👨‍💻 Developer Agent
- Writes clean, working Python code
- Uses test feedback for self-correction
- Iteratively improves code quality

### 🧪 QA Tester Agent
- Executes code in controlled environment using `exec()`
- Captures output and errors
- Provides detailed test reports for developer feedback

### 🔄 Router
- Decides workflow progression
- Routes failed tests back to developer
- Ends workflow on success or max iterations

## 🤝 Contributing

This is a demonstration project showing autonomous software development using LangGraph. Feel free to:

- Extend with additional agents (e.g., Code Reviewer, Security Auditor)
- Add support for different programming languages
- Implement more sophisticated testing strategies
- Enhance error handling and recovery mechanisms

## 📝 License

This project is provided as-is for educational and development purposes.

## 🐛 Troubleshooting

### "OpenAI API key not found"
- Ensure `.env` file exists and contains `OPENAI_API_KEY`
- Verify the API key is valid and has credits

### "Module not found" errors
- Activate the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt` (after creating one)

### Code execution fails repeatedly
- Check the `max_iterations` setting
- Review the test reports for specific error patterns
- Consider adjusting the LLM temperature or model

## 🔮 Future Enhancements

- [ ] Add support for multi-file projects
- [ ] Implement code review agent
- [ ] Add security scanning agent
- [ ] Support for different testing frameworks
- [ ] Web interface for monitoring workflow
- [ ] Integration with version control systems
- [ ] Deployment agent for production releases

---

Built with ❤️ using [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain)
