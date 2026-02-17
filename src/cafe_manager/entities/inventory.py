from dataclasses import dataclass
from enum import StrEnum

class Measure(StrEnum):
    LITER = "l"
    KILOGRAM = "kg"
    
class MenuItemType(StrEnum):
    DRINK = "drink"
    BEVERAGE = "beverage"

@dataclass
class Ingredient:
    name: str
    measure: Measure


@dataclass
class MenuItem:
    name: str
    ingredients: dict[Ingredient, float]
    cost: Money
    item_type: MenuItemType


class Menu:
    def __init__(self, menu_items: set[MenuItem] = None):
        self._drinks = set()
        self._beverage = set()
        for item in menu_items:
            self.add(item)

    def add(self, menu_item: MenuItem) -> None:
        if menu_item.item_type == "drink":
            self._drinks.add(menu_item)
        elif menu_item.item_type == "beverage":
            self._beverage.add(menu_item)

    def __str__(self) -> str:
        return f"DRINKS\n{self._drinks}\nBEVERAGE\n{self._beverage}"

    def remove(self, menu_item: MenuItem) -> None:
        if menu_item.item_type == "drink":
            self._drinks.remove(menu_item)
        elif menu_item.item_type == "beverage":
            self._beverage.remove(menu_item)