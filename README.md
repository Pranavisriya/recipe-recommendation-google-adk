# Recipe Recommendation Agent (Google ADK + LangGraph)

An end-to-end **AI-powered recipe recommendation assistant** built using **LangGraph** and **Google Agent Development Kit (ADK)**, following a clean, modular, agentic architecture.  
The system intelligently routes user requests, extracts ingredients, searches and ranks recipes, checks ingredient prices, and manages wallet balances through structured agent workflows.

## Prerequisites

- Python 3.12 or higher  
- uv (optional but recommended)  
- API keys for:
  - OpenAI
  - Google Generative AI (AI Studio)


## Installation

1. Clone the repository:
```bash
git clone https://github.com/Pranavisriya/recipe-recommendation-google-adk.git
cd recipe-recommendation-google-adk
```

2. Install `uv` in the environment if it is not present
```bash
pip install uv
```

3. Create a virtual python environment in this repo
```bash
uv init
uv venv -p 3.12
```

Any other method can also be used to create python environment.

4. Activate python environment
```bash
source .venv/bin/activate
```


5. Install dependencies using uv:
```bash
uv add -r requirements.txt
```

6. Create a `.env` file in the project root with your API keys:
```
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
```

## Usage
Run the tests:
```bash
pytest tests/
```
Run the project:
```bash
python main.py
```


## Features

- **ADK-based agent routing**
  - Routes user queries across recipe recommendations, ingredient pricing, and wallet operations
  - Central `root_agent` orchestrates task selection and execution

- **Recipe recommendation pipeline**
  - Natural language ingredient extraction
  - Recipe search from a structured CSV-backed dataset
  - Intelligent ranking based on ingredient overlap and suitability
  - LLM-generated personalized recommendations

- **Ingredient price lookup**
  - Queries structured ingredient price data
  - Enables budget-aware decision making

- **Wallet management**
  - User authentication via ID and PIN
  - Balance checks and deductions using CSV-backed wallet storage

- **LangGraph workflow**
  - Modular graph nodes for extract → search → rank → respond
  - Clean separation of logic for extensibility

  
## License

This project is licensed under the terms included in the LICENSE file.

## Author

Pranavi Sriya (pranavisriyavajha9@gmail.com)







