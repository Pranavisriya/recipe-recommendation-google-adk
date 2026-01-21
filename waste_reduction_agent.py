import os
from typing import List, Optional, Dict, Any
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from google.adk import Agent

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

class InventoryItem(BaseModel):
    ingredient: str = Field(..., description="Ingredient name")
    expiry_date: Optional[str] = Field(
        default=None,
        description="Optional expiry date in YYYY-MM-DD"
    )

class WasteInput(BaseModel):
    inventory: List[InventoryItem] = Field(default_factory=list)
    days_threshold: int = Field(default=5, description="Urgent if expiring within N days")
    max_cooking_time: Optional[int] = Field(default=None)
    cuisine_preference: Optional[str] = Field(default=None)

extractor = llm.with_structured_output(WasteInput)

EXTRACTION_SYSTEM = """Extract inventory + preferences from the user message.
Return ONLY valid JSON with:
{
  "inventory": [{"ingredient": string, "expiry_date": string|null}],
  "days_threshold": integer,
  "max_cooking_time": integer|null,
  "cuisine_preference": string|null
}

Rules:
- Include ONLY ingredients the user explicitly mentions.
- expiry_date ONLY if user explicitly provides a date; else null.
- days_threshold default 5; if user says "urgent/1-2 days" use 2-3.
- Do not invent items or dates.
"""


def parse_date(s: Optional[str]) -> Optional[date]:
    if not s or not isinstance(s, str) or not s.strip():
        return None
    try:
        return pd.to_datetime(s).date()
    except Exception:
        return None

def prioritize(inventory: List[Dict[str, Any]], days_threshold: int) -> Dict[str, Any]:
    today = date.today()
    urgent, non_urgent, unknown = [], [], []

    for item in inventory:
        ing = (item.get("ingredient") or "").strip().lower()
        exp_raw = item.get("expiry_date")
        exp = parse_date(exp_raw)

        if not ing:
            continue

        if exp is None:
            unknown.append({"ingredient": ing})
            continue

        days_left = (exp - today).days
        row = {"ingredient": ing, "expiry_date": exp.isoformat(), "days_left": days_left}
        if days_left <= days_threshold:
            urgent.append(row)
        else:
            non_urgent.append(row)

    urgent.sort(key=lambda x: x["days_left"])
    non_urgent.sort(key=lambda x: x["days_left"])
    return {"urgent": urgent, "non_urgent": non_urgent, "unknown_expiry": unknown}

def make_plan_text(plan: Dict[str, Any], cuisine: Optional[str], max_time: Optional[int]) -> str:
    prompt = f"""
You are a waste-reduction assistant. Create an actionable plan to reduce food waste.

Inventory classification:
- Urgent (use first): {plan["urgent"]}
- Unknown expiry: {plan["unknown_expiry"]}
- Non-urgent: {plan["non_urgent"]}

Preferences:
- Cuisine: {cuisine}
- Max cooking time: {max_time}

Return a concise response with EXACTLY these sections:

USE-FIRST (next {len(plan["urgent"])} items):
- <ingredient> (expires <date>, <days_left> days left)
...

ACTIONS (storage + prep):
- ...
- ...

2-DAY MINI PLAN:
Day 1: ...
Day 2: ...

Do NOT invent ingredients not in inventory.
"""
    resp = llm.invoke([SystemMessage(content=prompt)])
    return resp.content


def waste_reduction_tool(user_message: str) -> str:
    extracted = extractor.invoke(
        [{"role": "system", "content": EXTRACTION_SYSTEM},
         {"role": "user", "content": user_message}]
    )

    inventory = [{"ingredient": x.ingredient, "expiry_date": x.expiry_date} for x in extracted.inventory]
    if not inventory:
        return (
            "Tell me your inventory (and expiry dates if known). Example: "
            "'spinach expiring 2026-01-16, milk 2026-01-18, rice (no date)'."
        )

    plan = prioritize(inventory, extracted.days_threshold)
    return make_plan_text(plan, extracted.cuisine_preference, extracted.max_cooking_time)


waste_reduction_agent = Agent(
    name="waste_reduction_agent",
    description="Prioritizes expiring ingredients and suggests actions to reduce food waste.",
    tools=[waste_reduction_tool],
    instruction="""
You are the Waste Reduction Agent.
Always call waste_reduction_tool(user_message) first and return the tool output directly.
Never invent inventory items.
"""
)
