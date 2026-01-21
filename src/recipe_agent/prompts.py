EXTRACTION_SYSTEM = """You extract structured cooking preferences from a user message.
Return ONLY valid JSON (no markdown, no explanation) with keys:
{
  "ingredients": [string],
  "dietary_restrictions": [string],   // allowed: "vegetarian","vegan","gluten-free"
  "max_cooking_time": integer|null,   // minutes
  "cuisine_preference": string|null
}

Rules:
- Ingredients: list foods the user says they have (no quantities).
- If user doesn't specify something, use null (or [] for lists).
- Be conservative: don't invent ingredients.
"""
