import pytest
import json


@pytest.mark.asyncio
async def test_get_empty_recipes_list(test_client):
    response = await test_client.get("/recipes/")
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, list)
    assert content == []


@pytest.mark.asyncio
async def test_get_recipes_list_with_data(test_client, test_data):
    response = await test_client.get("/recipes/")
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, list)
    assert len(content) == len(test_data)
    expected = [
        {
            key: val
            for key, val in recipe.items()
            if key in ("title", "views_number", "cooking_time")
        }
        for recipe in test_data
    ]
    for recipe in content:
        assert recipe in expected


@pytest.mark.asyncio
async def test_post_new_recipe(test_client, test_data):
    test_recipe = test_data[0]
    response = await test_client.post("/recipes/", json=test_recipe)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert {
        key: val for key, val in content.items() if key != "id"
    } == test_recipe


@pytest.mark.asyncio
async def test_post_new_recipe_validation_error(test_client):
    test_recipe = {"title": "Bad Title" * 20, "recipe": "Good recipe"}
    response = await test_client.post("/recipes/", json=test_recipe)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert "100 characters" in json.dumps(content["detail"])


@pytest.mark.asyncio
async def test_get_recipe_by_id(test_client, test_data):
    test_id = 1
    response = await test_client.get(f"/recipes/{test_id}")
    content: dict = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert content["id"] == test_id
    expected = {
        key: val
        for key, val
        in test_data[test_id - 1].items()
        if key != "views_number"
    }
    assert {
        key: val for key, val in content.items() if key != "id"
    } == expected


@pytest.mark.asyncio
async def test_get_recipe_by_wrong_id(test_client, test_data):
    test_id = 9
    response = await test_client.get(f"/recipes/{test_id}")
    content: dict = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert f"id={test_id}" in content["detail"]


@pytest.mark.asyncio
async def test_get_recipe_by_id_validation_error(test_client, test_data):
    response = await test_client.get("/recipes/X")
    content: dict = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert "valid integer" in json.dumps(content["detail"])
