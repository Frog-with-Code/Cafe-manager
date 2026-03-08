from dataclasses import dataclass, field
from enum import StrEnum

from .finance import Money
from cafe_manager.common.exceptions import MenuItemTypeError


class Unit(StrEnum):
    LITER = "ml"
    KILOGRAM = "g"


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
    requires_milk_foam: bool
    ingredients: dict[Ingredient, float]
    
    def __hash__(self) -> int:
        return hash((
            self.requires_milk_foam,
            frozenset(self.ingredients.items())
        ))


@dataclass(frozen=True)
class MenuItem:
    name: str
    recipe: Recipe
    price: Money
    category: MenuItemCategory
    item_type: MenuItemType = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, 
            'item_type', 
            MenuItemType.DRINK if self.category in DRINKS_CATEGORIES else MenuItemType.FOOD
    )

    @property
    def requires_coffee_machine(self) -> bool:
        return self.category == MenuItemCategory.COFFEE

    @property
    def requires_milk_foam(self) -> bool:
        return self.recipe.requires_milk_foam


class Menu:
    def __init__(self, menu_items: set[MenuItem] | None = None, menu_id: int | None = None):
        self._drinks = set()
        self._food = set()
        self.menu_id = menu_id
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
        drinks_str = "\n".join(str(d) for d in self._drinks)
        food_str = "\n".join(str(f) for f in self._food)
        return f"DRINKS\n{drinks_str}\nFOOD\n{food_str}"
