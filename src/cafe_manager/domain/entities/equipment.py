import time
from enum import StrEnum
from rich.progress import track

from cafe_manager.common.exceptions import (
    RecipeError,
    CoffeeMachinePipelineError,
    CoffeeMachineStateError,
    TableCleaningError,
    TableOccupationError,
    TablePlacesError,
    TableStateError,
    ChairStateError,
)
from .menu import MenuItem


class TableState(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    DIRTY = "dirty"


class CoffeeMachineState(StrEnum):
    IDLE = "idle"
    GRINDING = "grinding"
    BREWING = "brewing"
    STEAMING = "steaming"
    MAINTENANCE = "maintenance"


class ChairState(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


class Chair:
    def __init__(
        self,
        chair_id: int | None = None,
        table_id: int | None = None,
        state: ChairState = ChairState.AVAILABLE,
    ) -> None:
        self.chair_id = chair_id
        self._table_id = table_id
        self._state = state

    def can_be_occupied(self) -> bool:
        return self._state == ChairState.AVAILABLE

    def occupy(self) -> None:
        if not self.can_be_occupied():
            raise ChairStateError("Chair is not available")

        self._state = ChairState.OCCUPIED
        print("Chair was occupied")

    def free(self) -> None:
        if self._state == ChairState.AVAILABLE:
            print("Chair is already available")
        else:
            self._state = ChairState.AVAILABLE
            print("Chair was released")

    def assign_to_table(self, table_id: int | None) -> None:
        if not isinstance(table_id, int):
            raise ValueError("Incorrect id type")
        self._table_id = table_id
        print(f"Chair {self.chair_id} was assigned to table {table_id}")


class Table:
    def __init__(
        self,
        max_places: int,
        state: TableState | None = None,
        table_id: int | None = None,
        chairs_ids: set[int] | None = None,
    ) -> None:
        self.table_id = table_id
        self.max_places = max_places
        self._state = state or TableState.AVAILABLE
        self._chairs_ids = chairs_ids or set()

    def clean(self) -> None:
        match (self._state):
            case TableState.AVAILABLE:
                print("Table is already clean")
            case TableState.OCCUPIED:
                raise TableCleaningError("Impossible to clean occupied table")
            case TableState.DIRTY:
                self._state = TableState.AVAILABLE
                print("Table was cleaned")
            case _:
                raise TableStateError("Unknown state")

    @property
    def is_available(self) -> bool:
        return self._state == TableState.AVAILABLE

    @property
    def chairs_ids(self) -> set[int]:
        return self._chairs_ids.copy()

    @property
    def chairs_amount(self) -> int:
        return len(self._chairs_ids)

    def can_be_occupied(self, people_amount: int) -> bool:
        return self.is_available and len(self._chairs_ids) >= people_amount

    def occupy(self, people_amount: int) -> None:
        if not self.can_be_occupied(people_amount):
            raise TableOccupationError(
                "Impossible to occupy table. It's not available or don't match the conditions"
            )
        self._state = TableState.OCCUPIED

    def free(self) -> None:
        match (self._state):
            case TableState.OCCUPIED:
                self._state = TableState.DIRTY
                print("Table was released")
            case TableState.AVAILABLE | TableState.DIRTY:
                print("Table is already free")
            case _:
                raise TableStateError("Unknown state")

    def add_chair(self, chair_id: int | None) -> None:
        if not isinstance(chair_id, int):
            raise ValueError("Incorrect id type")
        if self.chairs_amount >= self.max_places:
            raise TablePlacesError("Max places amount was already achieved")

        self._chairs_ids.add(chair_id)

    def remove_chair(self, chair_id: int | None) -> None:
        if not isinstance(chair_id, int):
            raise ValueError("Incorrect id type")
        try:
            self._chairs_ids.remove(chair_id)
        except KeyError:
            raise TablePlacesError(
                f"Chair with id {chair_id} not assigned to table {self.table_id}"
            )


class CoffeeMachine:
    PROGRESS_STEPS = 5
    PROGRESS_TOTAL = 100

    def __init__(self, model: str, maintenance_limit: int = 200) -> None:
        self.model = model
        self.maintenance_limit = maintenance_limit
        self.cycles_after_maintenance: int = 0
        self._state: CoffeeMachineState = CoffeeMachineState.IDLE

        self.grinding_time = 5
        self.brewing_time = 5
        self.steaming_time = 5

    def _grind(self) -> None:
        if self._state != CoffeeMachineState.IDLE:
            raise CoffeeMachinePipelineError(
                "Impossible to start grinding process. Coffee-machine is not ready to use"
            )

        self._state = CoffeeMachineState.GRINDING
        for _ in track(
            range(0, self.PROGRESS_TOTAL // self.PROGRESS_STEPS),
            description="Grinding...",
        ):
            time.sleep(self.grinding_time / self.PROGRESS_STEPS)

    def _brew(self) -> None:
        if self._state != CoffeeMachineState.GRINDING:
            raise CoffeeMachinePipelineError(
                "Impossible to start brewing process. Coffee beans were not grinded"
            )

        self._state = CoffeeMachineState.BREWING
        for _ in track(
            range(0, self.PROGRESS_TOTAL // self.PROGRESS_STEPS),
            description="Brewing...",
        ):
            time.sleep(self.brewing_time / self.PROGRESS_STEPS)

    def _steam(self) -> None:
        if self._state != CoffeeMachineState.BREWING:
            raise CoffeeMachinePipelineError(
                "Impossible to start steaming process. Coffee was not brewed"
            )

        self._state = CoffeeMachineState.STEAMING
        for _ in track(
            range(0, self.PROGRESS_TOTAL // self.PROGRESS_STEPS),
            description="Steaming...",
        ):
            time.sleep(self.steaming_time / self.PROGRESS_STEPS)

    def maintenance(self) -> None:
        match (self._state):
            case CoffeeMachineState.IDLE:
                print("Maintenance is not needed yet")
            case CoffeeMachineState.MAINTENANCE:
                self._state = CoffeeMachineState.IDLE
                self.cycles_after_maintenance = 0
            case (
                CoffeeMachineState.GRINDING
                | CoffeeMachineState.BREWING
                | CoffeeMachineState.STEAMING
            ):
                raise CoffeeMachineStateError(
                    "Impossible to carry out maintenance during working process"
                )
            case _:
                raise CoffeeMachineStateError("UnknownState")

    def make_coffee(self, coffee: MenuItem) -> None:
        if self._state != CoffeeMachineState.IDLE:
            raise CoffeeMachineStateError("Coffee-machine is not ready to use")
        if not coffee.requires_coffee_machine:
            raise RecipeError("No coffee-machine needed")
        self._grind()
        self._brew()
        if coffee.requires_milk_foam:
            self._steam()

        self._state = CoffeeMachineState.IDLE
        self.cycles_after_maintenance += 1
        print("Coffee is made!")
