## Recipe Recommendation (Google ADK + LangGraph)

This project is a **recipe recommendation assistant** built with:
- **LangGraph** for the internal recipe workflow (extract → search → rank → respond)
- **Google ADK** for agent routing (recipes, ingredient prices, wallet)

### Features
- **Recipe recommendations** from `src/recipe_agent/data/recipes.csv`
- **Ingredient price lookup** from `src/recipe_agent/data/ingredient_prices.csv`
- **Wallet checks/deductions** from `src/recipe_agent/data/wallet.csv`
- **ADK-based routing** via `src/recipe_agent/app.py` (`root_agent`)

### Project Structure
- `src/recipe_agent/app.py`: ADK agents + router (`root_agent`)
- `src/recipe_agent/graph.py`: LangGraph builder (LLM + nodes)
- `src/recipe_agent/runtime.py`: ADK Runner helpers (`create_session`, `call_adk`)
- `src/recipe_agent/nodes/`: graph nodes (extract/search/rank/generate)
- `src/recipe_agent/data/`: CSV-backed “database”
- `main.py`: CLI that runs through ADK (interactive chat)

### Setup
Create a `.env` file in the repo root:

```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

Install dependencies (choose one):

- **pip**:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- **uv** (optional, if you use it):

```bash
uv sync
```

### Run (ADK CLI)
From the repo root:

```bash
export PYTHONPATH=$PWD/src:$PYTHONPATH
set -a; source .env; set +a
python main.py
```

Example prompts:
- “I have rice and egg, suggest something Chinese”
- “Where can I buy rice cheaply?”
- “My user id is user_001 and pin is 1234. What is my balance?”

### Run Tests

```bash
export PYTHONPATH=$PWD/src:$PYTHONPATH
set -a; source .env; set +a
pytest
```

### Notes / Troubleshooting
- **`ModuleNotFoundError: recipe_agent`**:
  - Ensure `src/` is on `PYTHONPATH` (see run/test commands above).
- **Google key invalid**:
  - Make sure your `GOOGLE_API_KEY` is a valid **Generative Language / AI Studio** key and that `generativelanguage.googleapis.com` is enabled for that project.
- **NumPy 2.x warnings**:
  - Some optional dependencies may warn if they expect NumPy 1.x. If needed, pin NumPy with `numpy<2`.
