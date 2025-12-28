import sys
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

load_dotenv(".env_test")
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

RECIPES = [
    {
        "title": "Каша",
        "recipe": "Сварите кашу.",
        "views_number": 0,
        "cooking_time": 20,
        "ingredients": [
            {"title": "Крупа"},
            {"title": "Молоко"},
            {"title": "Соль (по вкусу)"}
        ]
    }, {
        "title": "Каша с маслом",
        "recipe": "Возьмите кашу. Добавьте масло.",
        "views_number": 1,
        "cooking_time": 21,
        "ingredients": [
            {"title": "Каша"},
            {"title": "Масло"}
        ]
    }
]

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..app.database import Base
from ..main import app, get_db
from ..app.models import Recipes, Ingredients

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def get_test_db():
    async with AsyncSessionLocal() as test_session:
        yield test_session


@pytest_asyncio.fixture()
async def test_client():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(
            transport=ASGITransport(app),
            base_url=os.getenv("API_URL")
    ) as client:
        yield client

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def test_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for full_dict in RECIPES:
                recipe_dict = {key: val for key, val in full_dict.items() if key != "ingredients"}
                recipe_obj = Recipes(**recipe_dict)
                recipe_obj.ingredients = [
                    Ingredients(title=ingredient["title"])
                    for ingredient
                    in full_dict["ingredients"]
                ]
                await session.merge(recipe_obj)
    yield RECIPES
