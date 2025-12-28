from typing import List

from pydantic import BaseModel, ConfigDict, Field


class BaseIngredient(BaseModel):
    title: str = Field(max_length=100)


class BaseRecipe(BaseModel):
    title: str = Field(max_length=100)
    cooking_time: int = Field(default=10)


class RecipeIn(BaseRecipe):
    views_number: int = Field(default=0)
    recipe: str
    ingredients: List[BaseIngredient]


class RecipeListOut(BaseRecipe):
    views_number: int

    model_config = ConfigDict(
        from_attributes=True
    )


class RecipeOut(BaseRecipe):
    id: int
    recipe: str
    ingredients: List[BaseIngredient]

    model_config = ConfigDict(
        from_attributes=True
    )


class RecipeOutFull(RecipeOut):
    views_number: int

    model_config = ConfigDict(
        from_attributes=True
    )
