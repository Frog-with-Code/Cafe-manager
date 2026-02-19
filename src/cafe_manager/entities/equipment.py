import time
from enum import StrEnum
from rich.progress import track

from cafe_manager.common.exceptions import (
    RecipeError,
    CoffeeMachinePipelineError,
    CoffeeMachineStateError,
    TableCleaningError,
    TableOccupationError,
    TableStateError,
)
from .menu import MenuItem


class TableStates(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    DIRTY = "dirty"


class CoffeeMachineState(StrEnum):
    IDLE = "idle"
    GRINDING = "grinding"
    BREWING = "brewing"
    STEAMING = "steaming"
    MAINTENANCE = "maintenance"


class Table:
    def __init__(self, place_amount: int) -> None:
        self.place_amount = place_amount
        self._state = TableStates.AVAILABLE

    def clean(self) -> None:
        match (self._state):
            case TableStates.AVAILABLE:
                print("Table is already clean")
            case TableStates.OCCUPIED:
                raise TableCleaningError("Impossible to clean occupied table")
            case TableStates.DIRTY:
                self._state = TableStates.AVAILABLE
                print("Table was cleaned")
            case _:
                raise TableStateError("Unknown state")

    def occupy(self) -> None:
        match (self._state):
            case TableStates.AVAILABLE:
                self._state = TableStates.OCCUPIED
                print("Table was occupied")
            case TableStates.OCCUPIED:
                raise TableOccupationError("Table is already occupied")
            case TableStates.DIRTY:
                raise TableOccupationError("Impossible to occupy dirty table")
            case _:
                raise TableStateError("Unknown state")

    def free(self) -> None:
        match (self._state):
            case TableStates.OCCUPIED:
                self._state = TableStates.DIRTY
                print("Table was released")
            case TableStates.AVAILABLE | TableStates.DIRTY:
                print("Table is already free")
            case _:
                raise TableStateError("Unknown state")


class CoffeeMachine:
    def __init__(self, model: str, maintenance_limit: int = 200) -> None:
        self.model = model
        self.maintenance_limit = maintenance_limit
        self.cycles_after_maintenance: int = 0
        self._state: CoffeeMachineState = CoffeeMachineState.IDLE

    def _grind(self) -> None:
        if self._state != CoffeeMachineState.IDLE:
            raise CoffeeMachinePipelineError(
                "Impossible to start grinding process. Coffee-machine is not ready to use"
            )

        self._state = CoffeeMachineState.GRINDING
        for _ in track(range(0, 100, 20), description="Grinding..."):
            time.sleep(0.5)

    def _brew(self) -> None:
        if self._state != CoffeeMachineState.GRINDING:
            raise CoffeeMachinePipelineError(
                "Impossible to start brewing process. Coffee beans were not grinded"
            )

        self._state = CoffeeMachineState.BREWING
        for _ in track(range(0, 100, 20), description="Brewing..."):
            time.sleep(0.5)

    def _steam(self) -> None:
        if self._state != CoffeeMachineState.BREWING:
            raise CoffeeMachinePipelineError(
                "Impossible to start steaming process. Coffee was not brewed"
            )

        self._state = CoffeeMachineState.STEAMING
        for _ in track(range(0, 100, 20), description="Steaming..."):
            time.sleep(0.5)

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

    def make_coffee(self, coffee: MenuItem) -> MenuItem:
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
