import pytest

from cafe_manager.entities.warehouse import Warehouse
from cafe_manager.common.exceptions import ImpossibleUnloading
from cafe_manager.entities.menu import Ingredient, Unit



@pytest.fixture
def milk():
    return Ingredient("Milk", Unit.LITER)

@pytest.fixture
def coffee():
    return Ingredient("Coffee", Unit.KILOGRAM)

@pytest.fixture
def empty_warehouse():
    return Warehouse()

@pytest.fixture
def warehouse_with_milk(milk):
    return Warehouse({milk: 100.0})


@pytest.fixture
def warehouse_with_multiple_ingredients(milk, coffee):
    """Фикстура для склада с несколькими ингредиентами"""
    return Warehouse({milk: 300.0, coffee: 50.0})


class TestWarehouseInit:
    def test_init_empty(self):
        warehouse = Warehouse()
        assert warehouse._stocks == {}

    def test_init_with_none(self):
        warehouse = Warehouse(None)
        assert warehouse._stocks == {}

    def test_init_with_data(self, milk):
        initial_data = {milk: 100.0}
        warehouse = Warehouse(initial_data)
        
        assert milk in warehouse._stocks
        assert warehouse._stocks[milk] == 100.0

    def test_init_independence(self, milk):
        data = {milk: 50.0}
        warehouse = Warehouse(data)
        
        assert warehouse._stocks is data 


class TestWarehouseSupply:
    def test_supply_new_ingredient(self, empty_warehouse, coffee):
        empty_warehouse.supply({coffee: 500.0})
        
        assert empty_warehouse._stocks[coffee] == 500.0

    def test_supply_existing_ingredient(self, warehouse_with_milk, milk):
        warehouse_with_milk.supply({milk: 50.0})
        
        assert warehouse_with_milk._stocks[milk] == 150.0

    def test_supply_multiple_ingredients(self, empty_warehouse, milk, coffee):
        empty_warehouse.supply({milk: 200.0, coffee: 500.0})
        
        assert empty_warehouse._stocks[milk] == 200.0
        assert empty_warehouse._stocks[coffee] == 500.0

    def test_supply_zero_amount(self, warehouse_with_milk, milk):
        warehouse_with_milk.supply({milk: 0.0})
        
        assert warehouse_with_milk._stocks[milk] == 100.0


class TestWarehouseWithdraw:
    def test_can_withdraw_success(self, warehouse_with_milk, milk):
        assert warehouse_with_milk.can_withdraw({milk: 50.0}) is True

    def test_can_withdraw_exact_amount(self, warehouse_with_milk, milk):
        """can_withdraw возвращает True, если запрашивается ровно столько, сколько есть"""
        assert warehouse_with_milk.can_withdraw({milk: 100.0}) is True

    def test_can_withdraw_not_enough_amount(self, warehouse_with_milk, milk):
        """can_withdraw возвращает False, если товара мало"""
        assert warehouse_with_milk.can_withdraw({milk: 150.0}) is False

    def test_can_withdraw_missing_ingredient(self, warehouse_with_milk, coffee):
        """can_withdraw возвращает False, если ингредиента нет на складе"""
        assert warehouse_with_milk.can_withdraw({coffee: 10.0}) is False

    def test_withdraw_success(self, warehouse_with_milk, milk):
        """withdraw успешно списывает ингредиенты"""
        warehouse_with_milk.withdraw({milk: 50.0})
        
        assert warehouse_with_milk._stocks[milk] == 50.0

    def test_withdraw_removes_zero_stock(self, warehouse_with_milk, milk):
        """withdraw удаляет ингредиент из словаря, если остаток 0"""
        warehouse_with_milk.withdraw({milk: 100.0})
        
        assert milk not in warehouse_with_milk._stocks

    def test_withdraw_raises_on_insufficient_stock(self, warehouse_with_milk, milk):
        """withdraw выбрасывает ImpossibleUnloading, если товара мало"""
        with pytest.raises(ImpossibleUnloading):
            warehouse_with_milk.withdraw({milk: 150.0})
        
        # Убедимся, что состояние не изменилось после ошибки
        assert warehouse_with_milk._stocks[milk] == 100.0

    def test_withdraw_raises_on_missing_ingredient(self, warehouse_with_milk, coffee):
        """withdraw выбрасывает ImpossibleUnloading, если ингредиента нет"""
        with pytest.raises(ImpossibleUnloading):
            warehouse_with_milk.withdraw({coffee: 10.0})

    def test_withdraw_multiple_ingredients(self, warehouse_with_multiple_ingredients, milk, coffee):
        """withdraw корректно работает с несколькими ингредиентами"""
        warehouse_with_multiple_ingredients.withdraw({milk: 100.0, coffee: 10.0})
        
        assert warehouse_with_multiple_ingredients._stocks[milk] == 200.0
        assert warehouse_with_multiple_ingredients._stocks[coffee] == 40.0