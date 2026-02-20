from .menu import Ingredient
from cafe_manager.common.exceptions import ImpossibleUnloading

class Warehouse:
    def __init__(self, ingredients: dict[Ingredient, float] = None) -> None:
        self._stocks = ingredients if ingredients else dict()

    def supply(self, ingredients: dict[Ingredient, float]) -> None:
        for ingredient, amount in ingredients.items():
            self._stocks[ingredient] = self._stocks.get(ingredient, 0) + amount

    def can_withdraw(self, ingredients: dict[Ingredient, float]) -> bool:
        if set(ingredients) - set(self._stocks):
            return False
        for ingredient, amount in ingredients.items():
            if self._stocks[ingredient] < amount:
                return False
        return True

    def withdraw(self, ingredients: dict[Ingredient, float]) -> None:
        if not self.can_withdraw(ingredients):
            raise ImpossibleUnloading("Not enough products in the warehouse")

        for ingredient, amount in ingredients.items():
            self._stocks[ingredient] -= amount
            if self._stocks[ingredient] == 0:
                del self._stocks[ingredient]