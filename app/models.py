from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Recipes(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    views_number = Column(Integer, index=True)
    cooking_time = Column(Integer, index=True)
    recipe = Column(Text, index=True)
    ingredients = relationship(
        "Ingredients",
        back_populates='recipe',
        cascade='all, delete-orphan',
        lazy='select'
    )


class Ingredients(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = relationship(
        "Recipes",
        back_populates="ingredients")
