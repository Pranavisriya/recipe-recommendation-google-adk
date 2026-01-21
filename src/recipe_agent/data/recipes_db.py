# RECIPES_DB = [
#     {"name": "Vegetable Fried Rice",
#      "ingredients": ["rice", "vegetables", "soy sauce", "garlic"],
#      "dietary": ["vegetarian"], "cuisine": "Asian", "cooking_time": 15},
#     {"name": "Veggie Rice Bowl",
#      "ingredients": ["rice", "vegetables", "beans", "avocado"],
#      "dietary": ["vegan", "gluten-free"], "cuisine": "Fusion", "cooking_time": 18},
#     {"name": "Mediterranean Rice Salad",
#      "ingredients": ["rice", "cucumber", "olive oil", "lemon"],
#      "dietary": ["vegan", "gluten-free"], "cuisine": "Mediterranean", "cooking_time": 20},
#     {"name": "Tofu Stir Fry",
#      "ingredients": ["tofu", "vegetables", "soy sauce", "ginger"],
#      "dietary": ["vegan"], "cuisine": "Asian", "cooking_time": 20},
#     {"name": "Egg Fried Rice",
#      "ingredients": ["rice", "eggs", "soy sauce", "peas"],
#      "dietary": ["vegetarian"], "cuisine": "Asian", "cooking_time": 12},
#     {"name": "Greek Salad",
#      "ingredients": ["cucumber", "tomato", "feta", "olive oil"],
#      "dietary": ["vegetarian", "gluten-free"], "cuisine": "Greek", "cooking_time": 10},
#     {"name": "Pasta Primavera",
#      "ingredients": ["pasta", "vegetables", "olive oil", "garlic"],
#      "dietary": ["vegetarian"], "cuisine": "Italian", "cooking_time": 25},
#     {"name": "Chickpea Curry",
#      "ingredients": ["chickpeas", "tomato", "onion", "spices"],
#      "dietary": ["vegan", "gluten-free"], "cuisine": "Indian", "cooking_time": 30},
#     {"name": "Chicken Rice Skillet",
#      "ingredients": ["chicken", "rice", "onion", "broth"],
#      "dietary": ["none"], "cuisine": "American", "cooking_time": 25},
#     {"name": "Lentil Soup",
#      "ingredients": ["lentils", "carrot", "celery", "onion"],
#      "dietary": ["vegan", "gluten-free"], "cuisine": "Comfort", "cooking_time": 35},
# ]

from __future__ import annotations
from typing import List, Dict, Any
import pandas as pd

from ..config import RECIPES_CSV, PRICES_CSV, WALLET_CSV

def load_recipes_db(path=RECIPES_CSV) -> List[Dict[str, Any]]:
    df = pd.read_csv(path)
    out: List[Dict[str, Any]] = []

    for _, r in df.iterrows():
        dietary = []
        if isinstance(r.get("dietary"), str) and r["dietary"].strip():
            dietary = [x.strip() for x in r["dietary"].split("|") if x.strip()]

        ingredients = [x.strip() for x in str(r["ingredients"]).split("|") if x.strip()]

        out.append({
            "id": int(r["id"]),
            "name": str(r["name"]),
            "cuisine": str(r["cuisine"]),
            "cooking_time": int(r["cooking_time"]),
            "dietary": dietary,
            "ingredients": ingredients,
            "instructions": str(r.get("instructions", "")),
        })

    return out

# Load once at import time (same idea as your RECIPES_DB)
RECIPES_DB = load_recipes_db()


# -------- Agent3 tool: ingredient prices --------
def get_best_ingredient_prices(ingredients: List[str]):
    df = pd.read_csv(PRICES_CSV)
    df["ingredient"] = df["ingredient"].astype(str).str.lower().str.strip()

    results = []
    for ing in ingredients:
        ing2 = ing.lower().strip()
        sub = df[df["ingredient"] == ing2]
        if sub.empty:
            results.append({"ingredient": ing2, "store": None, "price_usd": None, "unit": None})
        else:
            best = sub.sort_values("price_usd", ascending=True).iloc[0]
            results.append({
                "ingredient": ing2,
                "store": str(best["store"]),
                "price_usd": float(best["price_usd"]),
                "unit": str(best["unit"]),
            })
    return results


# -------- Agent4 tools: wallet --------
def authenticate_wallet(user_id: str, pin: str) -> bool:
    df = pd.read_csv(WALLET_CSV)
    row = df[df["user_id"] == user_id]
    return (not row.empty) and (str(row.iloc[0]["pin"]) == str(pin))

def get_wallet_balance(user_id: str) -> float:
    df = pd.read_csv(WALLET_CSV)
    row = df[df["user_id"] == user_id]
    return float(row.iloc[0]["balance_usd"])

def deduct_wallet(user_id: str, amount: float) -> float:
    df = pd.read_csv(WALLET_CSV)
    idx = df.index[df["user_id"] == user_id]
    if len(idx) == 0:
        raise ValueError("User not found")
    i = idx[0]

    bal = float(df.loc[i, "balance_usd"])
    if amount > bal:
        raise ValueError("Insufficient funds")

    df.loc[i, "balance_usd"] = round(bal - amount, 2)
    df.to_csv(WALLET_CSV, index=False)
    return float(df.loc[i, "balance_usd"])
