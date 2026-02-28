import pytest
from dataclasses import dataclass

# Предполагаемые импорты из вашего проекта:
from cafe_manager.common.exceptions import ImpossibleUnloading
from cafe_manager.domain.services.inventory_service import InventoryService
from cafe_manager.domain.entities.menu import Ingredient, Unit


class TestInventoryService:
    
    @pytest.fixture
    def service(self):
        return InventoryService()

    @pytest.fixture
    def tomato(self): return Ingredient("Tomato", Unit.KILOGRAM)

    @pytest.fixture
    def cheese(self): return Ingredient("Cheese", Unit.KILOGRAM)

    @pytest.fixture
    def dough(self):  return Ingredient("Dough", Unit.LITER)


    def test_can_withdraw_success(self, service, tomato, cheese):
        stocks = {tomato: 10.0, cheese: 5.0}
        write_offs = {tomato: 3.0, cheese: 5.0}
        
        assert service.can_withdraw(stocks, write_offs) is True

    def test_can_withdraw_not_enough_stock(self, service, tomato, cheese):
        stocks = {tomato: 10.0, cheese: 5.0}
        write_offs = {tomato: 12.0, cheese: 2.0}
        
        assert service.can_withdraw(stocks, write_offs) is False

    def test_can_withdraw_missing_ingredient(self, service, dough):
        stocks = {}
        write_offs = {dough: 1.0}
        
        assert service.can_withdraw(stocks, write_offs) is False

    def test_can_withdraw_empty_write_offs(self, service, tomato):
        stocks = {tomato: 10.0}
        assert service.can_withdraw(stocks, {}) is True

    def test_withdraw_success_calculation(self, service, tomato, cheese, dough):
        stocks = {tomato: 10.0, cheese: 5.0, dough: 2.0}
        write_offs = {tomato: 4.0, cheese: 5.0} 
        
        result = service.withdraw(stocks, write_offs)
        
        assert result[tomato] == 6.0
        assert result[cheese] == 0.0 
        assert result[dough] == 2.0  
        assert len(result) == 3      

    def test_withdraw_creates_new_dict(self, service, tomato):
        stocks = {tomato: 10.0}
        write_offs = {tomato: 2.0}
        
        result = service.withdraw(stocks, write_offs)
        
        assert result is not stocks
        assert stocks[tomato] == 10.0

    def test_withdraw_raises_exception(self, service, tomato):
        stocks = {tomato: 5.0}
        write_offs = {tomato: 10.0}
        
        with pytest.raises(ImpossibleUnloading, match="Not enough products to withdraw"):
            service.withdraw(stocks, write_offs)

    def test_withdraw_with_empty_write_offs(self, service, tomato):
        stocks = {tomato: 5.0}
        
        result = service.withdraw(stocks, {})
        
        assert result == stocks
        assert result is not stocks