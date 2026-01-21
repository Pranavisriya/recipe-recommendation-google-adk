from __future__ import annotations
from pathlib import Path

# project: .../src/recipe_agent/config.py
PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"

RECIPES_CSV = DATA_DIR / "recipes.csv"
PRICES_CSV = DATA_DIR / "ingredient_prices.csv"
WALLET_CSV = DATA_DIR / "wallet.csv"
