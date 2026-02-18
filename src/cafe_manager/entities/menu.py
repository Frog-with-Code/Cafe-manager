from dataclasses import dataclass, field
from enum import StrEnum

from .finance import Money
from cafe_manager.common.exceptions import MenuItemTypeError


class Unit(StrEnum):
    LITER = "l"
    KILOGRAM = "kg"


class MenuItemType(StrEnum):
    DRINK = "drink"
    FOOD = "food"


class MenuItemCategory(StrEnum):
    COFFEE = "coffee"
    TEA = "tea"
    COCKTAIL = "cocktail"
    SMOOTHIE = "smoothie"
    BAKERY = "bakery"
    SOUP = "soup"


DRINKS_CATEGORIES: set[MenuItemCategory] = {
    MenuItemCategory.COFFEE,
    MenuItemCategory.TEA,
    MenuItemCategory.COCKTAIL,
    MenuItemCategory.SMOOTHIE,
}


@dataclass(frozen=True)
class Ingredient:
    name: str
    unit: Unit


@dataclass(frozen=True)
class Recipe:
    cook_time_seconds: int
    requires_milk_foam: bool
    ingredients: dict[Ingredient, float] = field(default_factory=dict)


@dataclass
class MenuItem:
    name: str
    recipe: Recipe
    price: Money
    category: MenuItemCategory
    item_type: MenuItemType = field(init=False)

    def __post_init__(self) -> None:
        self.item_type = (
            MenuItemType.DRINK
            if self.category in DRINKS_CATEGORIES
            else MenuItemType.FOOD
        )

    @property
    def requires_coffee_machine(self) -> bool:
        return self.category == MenuItemCategory.COFFEE

    @property
    def requires_milk_foam(self) -> bool:
        return self.recipe.requires_milk_foam
    
    def __hash__(self):
        return hash(self.name)


class Menu:
    def __init__(self, menu_items: set[MenuItem] = None):
        self._drinks = set()
        self._food = set()
        if menu_items:
            for item in menu_items:
                self.add(item)

    def add(self, menu_item: MenuItem) -> None:
        if menu_item.item_type == MenuItemType.DRINK:
            self._drinks.add(menu_item)
        elif menu_item.item_type == MenuItemType.FOOD:
            self._food.add(menu_item)
        else:
            raise MenuItemTypeError("Unknown type of the menu item")

    def remove(self, menu_item: MenuItem) -> None:
        if menu_item.item_type == MenuItemType.DRINK:
            self._drinks.remove(menu_item)
        elif menu_item.item_type == MenuItemType.FOOD:
            self._food.remove(menu_item)
        else:
            raise MenuItemTypeError("Unknown type of the menu item")

    def __str__(self) -> str:
        return f"DRINKS\n{self._drinks.copy()}\nFOOD\n{self._food.copy()}"
