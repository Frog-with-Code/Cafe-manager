from ..entities.menu import Ingredient
from cafe_manager.common.exceptions import ImpossibleUnloading


class InventoryService:
    def supply(
        self, stocks: dict[Ingredient, float], restocks: dict[Ingredient, float]
    ) -> dict[Ingredient, float]:
        for ingredient, amount in restocks.items():
            stocks[ingredient] = stocks.get(ingredient, 0) + amount
        return stocks

    def can_withdraw(
        self, stocks: dict[Ingredient, float], write_offs: dict[Ingredient, float]
    ) -> bool:
        return all(
            stocks.get(ingredient, 0) >= amount
            for ingredient, amount in write_offs.items()
        )

    def withdraw(
        self, stocks: dict[Ingredient, float], write_offs: dict[Ingredient, float]
    ) -> dict[Ingredient, float]:
        if not self.can_withdraw(stocks, write_offs):
            raise ImpossibleUnloading("Not enough products to withdraw")

        return {
            key: stocks.get(key, 0) - write_offs.get(key, 0)
            for key in stocks.keys() | write_offs.keys()
        }
