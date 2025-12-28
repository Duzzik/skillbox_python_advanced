from typing import List

from fastapi import FastAPI, Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from sqlalchemy.orm import selectinload

import app.models as models
import app.schemas as schemas
from app.database import get_db, create_tables


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path
        }
    )


@app.get('/recipes/', response_model=List[schemas.RecipeListOut])
async def list_recipes(
        db: AsyncSession = Depends(get_db)
) -> List[models.Recipes]:
    async with db.begin():
        result = await db.execute(select(models.Recipes))
    return list(result.scalars().all())


@app.post('/recipes/', response_model=schemas.RecipeOutFull)
async def add_recipes(
        recipe_data: schemas.RecipeIn,
        db: AsyncSession = Depends(get_db)
) -> models.Recipes:
    data_dict = recipe_data.model_dump()

    recipe_dict = {key: val for key, val in data_dict.items() if key != "ingredients"}
    recipe_obj = models.Recipes(**recipe_dict)
    recipe_obj.ingredients = [
        models.Ingredients(title=ingredient["title"])
        for ingredient
        in data_dict["ingredients"]
    ]

    try:
        async with db.begin():
            merged_recipe = await db.merge(recipe_obj)
        return merged_recipe
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )


@app.get('/recipes/{recipe_id}', response_model=schemas.RecipeOut)
async def recipe_by_id(
        recipe_id: int,
        db: AsyncSession = Depends(get_db)
) -> type[models.Recipes]:
    async with (db.begin()):
        query = select(models.Recipes)\
            .options(selectinload(models.Recipes.ingredients))\
            .where(models.Recipes.id == recipe_id)
        query_result = await db.execute(query)
        result = query_result.scalar_one_or_none()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id={recipe_id} not found"
        )
    return result
