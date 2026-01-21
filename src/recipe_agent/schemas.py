from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    ingredients: List[str] = Field(default_factory=list, description="Ingredients the user has")
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description='Allowed: "vegetarian", "vegan", "gluten-free"'
    )
    max_cooking_time: Optional[int] = Field(default=None, description="Minutes")
    cuisine_preference: Optional[str] = Field(default=None, description="Cuisine name, if any")
