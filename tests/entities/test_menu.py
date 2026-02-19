import pytest

from cafe_manager.entities.menu import (
    Unit,
    MenuItemType,
    MenuItemCategory,
    Ingredient,
    Recipe,
    MenuItem,
    Menu,
)
from cafe_manager.entities.finance import Money


@pytest.fixture
def money():
    return Money(amount=100, currency="RUB")


@pytest.fixture
def ingredient():
    return Ingredient(name="Water", unit=Unit.LITER)


@pytest.fixture
def recipe():
    return Recipe(
        ingredients={Ingredient(name="Coffee Beans", unit=Unit.KILOGRAM): 0.05},
        cook_time_seconds=60,
        requires_milk_foam=True,
    )


@pytest.fixture
def coffee_item(money, recipe):
    return MenuItem(
        name="Latte", recipe=recipe, price=money, category=MenuItemCategory.COFFEE
    )


@pytest.fixture
def tea_item(money, recipe):
    return MenuItem(
        name="Black Tea", recipe=recipe, price=money, category=MenuItemCategory.TEA
    )


class TestIngredient:
    def test_ingredient_creation(self):
        ing = Ingredient(name="Milk", unit=Unit.LITER)
        assert ing.name == "Milk"
        assert ing.unit == Unit.LITER


class TestRecipe:
    def test_recipe_creation(self):
        ingredients = {Ingredient("Sugar", Unit.KILOGRAM): 10.0}
        recipe = Recipe(
            ingredients=ingredients, cook_time_seconds=30, requires_milk_foam=False
        )
        assert recipe.cook_time_seconds == 30
        assert recipe.requires_milk_foam is False
        assert Ingredient("Sugar", Unit.KILOGRAM) in recipe.ingredients


class TestMenuItem:
    def test_menu_item_drink_type_inference(self, coffee_item):
        assert coffee_item.item_type == MenuItemType.DRINK

    def test_menu_item_category_coffee(self, coffee_item):
        assert coffee_item.category == MenuItemCategory.COFFEE
        assert coffee_item.requires_coffee_machine is True

    def test_menu_item_category_tea(self, tea_item):
        assert tea_item.item_type == MenuItemType.DRINK
        assert tea_item.category == MenuItemCategory.TEA
        assert tea_item.requires_coffee_machine is False

    def test_menu_item_requires_milk_foam(self, coffee_item):
        assert coffee_item.requires_milk_foam is True


class TestMenu:
    def test_menu_initialization_empty(self):
        menu = Menu(menu_items=set())
        assert len(menu._drinks) == 0
        assert len(menu._food) == 0

    def test_menu_initialization_with_items(self, coffee_item, tea_item):
        menu = Menu(menu_items={coffee_item, tea_item})
        assert len(menu._drinks) == 2
        assert coffee_item in menu._drinks
        assert tea_item in menu._drinks

    def test_menu_add_drink(self, coffee_item):
        menu = Menu(set())
        menu.add(coffee_item)
        assert coffee_item in menu._drinks
        assert len(menu._food) == 0

    def test_menu_remove_drink(self, coffee_item):
        menu = Menu({coffee_item})
        menu.remove(coffee_item)
        assert coffee_item not in menu._drinks
        assert len(menu._drinks) == 0

    def test_menu_str_representation(self, coffee_item):
        menu = Menu({coffee_item})
        str_repr = str(menu)
        assert "DRINKS" in str_repr
        assert "FOOD" in str_repr
        assert coffee_item.name in str_repr

    def test_menu_init_without_arguments_should_handle_none(self):
        menu = Menu()
        assert len(menu._drinks) == 0
