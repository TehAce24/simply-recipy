import pytest
from simply_recipy import api_recipe_by_ingredients, join_items, valid_items, save_recipe
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key")
base_url = "https://api.spoonacular.com/"


def test_api_status():
    wrong_key = ""
    wrong_url = "https://api.spoonacular.com/error"
    test = api_recipe_by_ingredients("apple", base_url, api_key)
    assert test.status_code == 200
    with pytest.raises(Exception):
        api_recipe_by_ingredients("apple", base_url, wrong_key)
    with pytest.raises(Exception):
        api_recipe_by_ingredients("apple", wrong_url, api_key)


def test_join_items():
    assert join_items(['apple', 'banana']) == 'apple,banana'
    assert join_items(['apple', 'banana', 'cherry']) == 'apple,banana,cherry'
    assert join_items(['2', '4', '5']) == '2,4,5'


def test_valid_items():
    assert valid_items(['apple', 'banana']) == True
    assert valid_items(['apple', 'banana', 'cherry']) == True
    assert valid_items(['4pple', 'banana']) == False
    assert valid_items(['apple', '']) == False
    assert valid_items(['123', '', 'apple']) == False


def test_save_recipe():
    filename = "testfile"
    save_recipe(filename)
    assert os.path.isfile(f"{filename}.txt")

    invalid_file = "invalid\\file"
    assert os.path.isfile(f"{invalid_file}.txt") == False
