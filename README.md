# Agent_ai

A collection of local AI agent scripts for Streamlit, Groq, LangChain, Agno, and SQL-based workflows.

## Repository Contents

- `agent1.py` - Streamlit dashboard with a Groq-powered SQL assistant, local SQLite database, and LangGraph workflow.
- `simplaeagent.py` - Example Agno agent with calculator and mock API tools.
- `sql.py` - SQL execution agent using LangChain, SQLAlchemy, and ChatOpenAI.
- `sql2.py` - Multi-agent example with CrewAI/Agno, Pandas and code interpreter tools.
- `webagent.py` - Orchestrator team agent with build/finance/marketing/web search specialists using Agno.
- `.env` - environment variables for API keys (not tracked in git).
- `nexus_students.db` - local sample SQLite database.

## Quick Start

1. Install Python 3.11+.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows
   # or
   source venv/bin/activate      # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the repository root with your API keys, for example:
   ```text
   GROQ_API_KEY=your_groq_api_key
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## Running Examples

- Streamlit dashboard:
  ```bash
  streamlit run agent1.py
  ```

- Run a simple agent example:
  ```bash
  python simplaeagent.py
  ```

- Run other agent scripts:
  ```bash
  python sql.py
  python sql2.py
  python webagent.py
  ```

## Notes

- The repository already includes `.gitignore` to exclude `env/`, `venv/`, and `.env` files.
- Keep your API keys secret and do not commit them to GitHub.
- Some scripts depend on external services and may require valid API keys.

## License

Add a license file if you want to make the project open source.
