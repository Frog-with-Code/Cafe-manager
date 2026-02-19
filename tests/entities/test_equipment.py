import pytest

from cafe_manager.entities.equipment import (
    Table,
    CoffeeMachine,
    TableStates,
    CoffeeMachineState,
)
from cafe_manager.common.exceptions import (
    RecipeError,
    CoffeeMachinePipelineError,
    CoffeeMachineStateError,
    TableCleaningError,
    TableOccupationError,
    TableStateError,
)


class TestTable:
    @pytest.fixture
    def table(self):
        return Table(place_amount=4)

    def test_table_initial_state(self, table):
        assert table.place_amount == 4
        assert table._state in [TableStates.AVAILABLE, "free"]

    def test_clean_available_table(self, table, capsys):
        table._state = TableStates.AVAILABLE
        table.clean()
        captured = capsys.readouterr()
        assert "Table is already clean" in captured.out
        assert table._state == TableStates.AVAILABLE

    def test_clean_occupied_table_raises_error(self, table):
        table._state = TableStates.OCCUPIED
        with pytest.raises(TableCleaningError, match="Impossible to clean occupied table"):
            table.clean()

    def test_clean_dirty_table(self, table, capsys):
        table._state = TableStates.DIRTY
        table.clean()
        assert table._state == TableStates.AVAILABLE

    def test_occupy_available_table(self, table, capsys):
        table._state = TableStates.AVAILABLE
        table.occupy()
        assert table._state == TableStates.OCCUPIED

    def test_occupy_occupied_table_raises_error(self, table):
        table._state = TableStates.OCCUPIED
        with pytest.raises(TableOccupationError, match="Table is already occupied"):
            table.occupy()

    def test_occupy_dirty_table_raises_error(self, table):
        table._state = TableStates.DIRTY
        with pytest.raises(TableOccupationError, match="Impossible to occupy dirty table"):
            table.occupy()

    def test_free_occupied_table(self, table, capsys):
        table._state = TableStates.OCCUPIED
        table.free()
        assert table._state == TableStates.DIRTY

    def test_free_available_table(self, table, capsys):
        table._state = TableStates.AVAILABLE
        table.free()
        captured = capsys.readouterr()
        assert "Table is already free" in captured.out
        assert table._state == TableStates.AVAILABLE

    def test_free_dirty_table(self, table, capsys):
        table._state = TableStates.DIRTY
        table.free()
        captured = capsys.readouterr()
        assert "Table is already free" in captured.out
        assert table._state == TableStates.DIRTY

    def test_table_unknown_state_clean(self, table):
        table._state = "UNKNOWN_STATE"
        with pytest.raises(TableStateError, match="Unknown state"):
            table.clean()

    def test_table_unknown_state_occupy(self, table):
        table._state = "UNKNOWN_STATE"
        with pytest.raises(TableStateError, match="Unknown state"):
            table.occupy()

    def test_table_unknown_state_free(self, table):
        table._state = "UNKNOWN_STATE"
        with pytest.raises(TableStateError, match="Unknown state"):
            table.free()


class TestCoffeeMachine:
    @pytest.fixture
    def coffee_machine(self):
        return CoffeeMachine(model="TestModel", maintenance_limit=200)

    def test_coffee_machine_initial_state(self, coffee_machine):
        assert coffee_machine.model == "TestModel"
        assert coffee_machine.maintenance_limit == 200
        assert coffee_machine.cycles_after_maintenance == 0
        assert coffee_machine._state == CoffeeMachineState.IDLE

    def test_grind_from_idle(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.IDLE
        coffee_machine._grind()
        
        assert coffee_machine._state == CoffeeMachineState.GRINDING

    def test_grind_from_wrong_state(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.BREWING
        with pytest.raises(CoffeeMachinePipelineError, match="Coffee-machine is not ready to use"):
            coffee_machine._grind()

    def test_brew_from_grinding(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.GRINDING
        coffee_machine._brew()
        
        assert coffee_machine._state == CoffeeMachineState.BREWING

    def test_brew_from_wrong_state(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.IDLE
        with pytest.raises(CoffeeMachinePipelineError, match="Coffee beans were not grinded"):
            coffee_machine._brew()

    def test_steam_from_brewing(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.BREWING
        coffee_machine._steam()
        
        assert coffee_machine._state == CoffeeMachineState.STEAMING

    def test_steam_from_wrong_state(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.GRINDING
        with pytest.raises(CoffeeMachinePipelineError, match="Coffee was not brewed"):
            coffee_machine._steam()

    def test_maintenance_when_idle(self, coffee_machine, capsys):
        coffee_machine._state = CoffeeMachineState.IDLE
        coffee_machine.maintenance()
        captured = capsys.readouterr()
        assert "Maintenance is not needed yet" in captured.out

    def test_maintenance_from_maintenance_state(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.MAINTENANCE
        coffee_machine.cycles_after_maintenance = 50
        
        coffee_machine.maintenance()
        
        assert coffee_machine._state == CoffeeMachineState.IDLE
        assert coffee_machine.cycles_after_maintenance == 0

    @pytest.mark.parametrize("state", [
        CoffeeMachineState.GRINDING,
        CoffeeMachineState.BREWING,
        CoffeeMachineState.STEAMING
    ])
    def test_maintenance_during_work_raises_error(self, coffee_machine, state):
        coffee_machine._state = state
        with pytest.raises(CoffeeMachineStateError, match="during working process"):
            coffee_machine.maintenance()

    def test_make_coffee_success(self, coffee_machine, mocker):
        coffee_machine._state = CoffeeMachineState.IDLE
        mock_menu_item = mocker.Mock()
        mock_menu_item.requires_milk_foam = False
        
        coffee_machine.make_coffee(mock_menu_item)
        
        assert coffee_machine._state == CoffeeMachineState.IDLE
        assert coffee_machine.cycles_after_maintenance == 1

    def test_make_coffee_with_foam(self, coffee_machine, mocker):
        coffee_machine._state = CoffeeMachineState.IDLE
        mock_menu_item = mocker.Mock()
        mock_menu_item.requires_coffee_foam = True
        mock_steam = mocker.patch.object(CoffeeMachine, "_steam")
        
        coffee_machine.make_coffee(mock_menu_item)
        
        assert coffee_machine.cycles_after_maintenance == 1
        mock_steam.assert_called_once()

    def test_make_coffee_machine_not_ready(self, coffee_machine, mocker):
        coffee_machine._state = CoffeeMachineState.BREWING
        mock_item = mocker.Mock()
        
        with pytest.raises(CoffeeMachineStateError, match="not ready to use"):
            coffee_machine.make_coffee(mock_item)

    def test_make_coffee_not_required(self, coffee_machine, mocker):
        mock_menu_item = mocker.Mock()
        mock_menu_item.requires_coffee_machine = False
        
        with pytest.raises(RecipeError, match="No coffee-machine needed"):
            coffee_machine.make_coffee(mock_menu_item)