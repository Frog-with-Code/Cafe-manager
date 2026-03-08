import pytest
from uuid import uuid4, UUID

from cafe_manager.domain.entities.equipment import (
    Table,
    CoffeeMachine,
    TableState,
    CoffeeMachineState,
    Chair,
    ChairState,
)
from cafe_manager.common.exceptions import (
    RecipeError,
    CoffeeMachinePipelineError,
    CoffeeMachineStateError,
    TableCleaningError,
    TableOccupationError,
    TablePlacesError,
    ChairStateError,
)


class TestTable:
    @pytest.fixture
    def table(self) -> Table:
        return Table(table_id=11, max_places=4)

    @pytest.fixture
    def table_with_chairs(self, table: Table) -> Table:
        table.add_chair(111)
        table.add_chair(222)
        return table

    def test_initialization(self, table: Table):
        assert table.max_places == 4
        assert table.is_available is True
        assert isinstance(table.table_id, int)
        assert table.chairs_amount == 0
        assert table.chairs_ids == set()

    def test_chairs_id_encapsulation(self, table: Table):
        table.add_chair(3)
        chairs_copy = table.chairs_ids

        chairs_copy.add(4)

        assert table.chairs_amount == 1
        assert len(chairs_copy) == 2

    def test_add_chair_success(self, table: Table):
        chair_id = 3
        table.add_chair(chair_id)

        assert table.chairs_amount == 1
        assert chair_id in table.chairs_ids

    def test_add_chair_exceeds_max_places(self, table: Table):
        for i in range(4):
            table.add_chair(i)

        with pytest.raises(
            TablePlacesError, match="Max places amount was already achieved"
        ):
            table.add_chair(4)

    def test_remove_chair_success(self, table: Table):
        chair_id = 3
        table.add_chair(chair_id)
        table.remove_chair(chair_id)

        assert table.chairs_amount == 0

    def test_remove_nonexistent_chair(self, table: Table):
        fake_chair_id = 3
        with pytest.raises(
            TablePlacesError, match=f"not assigned to table {table.table_id}"
        ):
            table.remove_chair(fake_chair_id)

    def test_can_be_occupied_true(self, table_with_chairs: Table):
        assert table_with_chairs.can_be_occupied(people_amount=2) is True
        assert table_with_chairs.can_be_occupied(people_amount=1) is True

    def test_can_be_occupied_false_not_enough_chairs(self, table_with_chairs: Table):
        assert table_with_chairs.can_be_occupied(people_amount=3) is False

    def test_can_be_occupied_false_not_free(self, table_with_chairs: Table):
        table_with_chairs._state = TableState.DIRTY
        assert table_with_chairs.can_be_occupied(people_amount=2) is False

    def test_occupy_raises_error(self, table_with_chairs: Table):
        with pytest.raises(TableOccupationError):
            table_with_chairs.occupy(people_amount=5)

    def test_occupy_success(self, table_with_chairs: Table):
        table_with_chairs.occupy(people_amount=2)

    def test_free_occupied_table(self, table: Table, capsys):
        table._state = TableState.OCCUPIED
        table.free()

        assert table._state == TableState.DIRTY
        assert "Table was released" in capsys.readouterr().out

    @pytest.mark.parametrize("initial_state", [TableState.AVAILABLE, TableState.DIRTY])
    def test_free_already_free_or_dirty(
        self, table: Table, initial_state: TableState, capsys
    ):
        table._state = initial_state
        table.free()

        assert table._state == initial_state
        assert "Table is already free" in capsys.readouterr().out

    def test_clean_dirty_table(self, table: Table):
        table._state = TableState.DIRTY
        table.clean()

        assert table._state == TableState.AVAILABLE

    def test_clean_occupied_table_raises_error(self, table: Table):
        table._state = TableState.OCCUPIED
        with pytest.raises(
            TableCleaningError, match="Impossible to clean occupied table"
        ):
            table.clean()

    def test_clean_already_available_table(self, table: Table, capsys):
        table._state = TableState.AVAILABLE
        table.clean()

        assert table._state == TableState.AVAILABLE
        assert "Table is already clean" in capsys.readouterr().out


class TestChair:
    @pytest.fixture
    def chair(self) -> Chair:
        return Chair(chair_id=1)

    def test_initialization(self, chair: Chair):
        assert isinstance(chair.chair_id, int)
        assert chair._table_id is None
        assert chair._state == ChairState.AVAILABLE
        assert chair.can_be_occupied() is True

    def test_assign_to_table(self, chair: Chair):
        table_id = 2
        chair.assign_to_table(table_id)

        assert chair._table_id == table_id

    def test_can_be_occupied(self, chair: Chair):
        assert chair.can_be_occupied() is True

        chair._state = ChairState.OCCUPIED
        assert chair.can_be_occupied() is False

    def test_occupy_success(self, chair: Chair):
        chair.occupy()

        assert chair._state == ChairState.OCCUPIED
        assert chair.can_be_occupied() is False

    def test_occupy_already_occupied_raises_error(self, chair: Chair):
        chair.occupy()

        with pytest.raises(ChairStateError, match="Chair is not available"):
            chair.occupy()

    def test_free_occupied_chair(self, chair: Chair):
        chair.occupy()

        chair.free()

        assert chair._state == ChairState.AVAILABLE

    def test_free_already_available_chair(self, chair: Chair, capsys):
        chair.free()

        assert chair._state == ChairState.AVAILABLE
        captured = capsys.readouterr()
        assert "Chair is already available\n" in captured.out


class TestCoffeeMachine:
    @pytest.fixture
    def coffee_machine(self):
        machine = CoffeeMachine(model="TestModel", maintenance_limit=200)
        machine.grinding_time = 0
        machine.brewing_time = 0
        machine.steaming_time = 0
        return machine

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
        with pytest.raises(
            CoffeeMachinePipelineError, match="Coffee-machine is not ready to use"
        ):
            coffee_machine._grind()

    def test_brew_from_grinding(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.GRINDING
        coffee_machine._brew()

        assert coffee_machine._state == CoffeeMachineState.BREWING

    def test_brew_from_wrong_state(self, coffee_machine):
        coffee_machine._state = CoffeeMachineState.IDLE
        with pytest.raises(
            CoffeeMachinePipelineError, match="Coffee beans were not grinded"
        ):
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

    @pytest.mark.parametrize(
        "state",
        [
            CoffeeMachineState.GRINDING,
            CoffeeMachineState.BREWING,
            CoffeeMachineState.STEAMING,
        ],
    )
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
