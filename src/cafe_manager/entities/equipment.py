from ..common.exceptions import *
from enum import StrEnum
import time
from rich.progress import track


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
        self._state = TableStates.FREE

    def clean(self) -> None:
        match (self._state):
            case "available":
                print("Table is already clean")
            case "occupied":
                raise TableCleaningError("Impossible to clean occupied table")
            case "dirty":
                self._state = TableStates.AVAILABLE
                print("Table was cleaned")
            case _:
                raise TableStateError("Unknown state")

    def occupy(self) -> None:
        match (self._state):
            case "available":
                self._state = TableStates.OCCUPIED
                print("Table was occupied")
            case "occupied":
                raise TableOccupationError("Table is already occupied")
            case "dirty":
                raise TableOccupationError("Impossible to occupy dirty table")
            case _:
                raise TableStateError("Unknown state")

    def free(self) -> None:
        match (self._state):
            case "occupied":
                self._state = "dirty"
                print("Table was released")
            case "available" | "dirty":
                print("Table is already free")
            case _:
                raise TableStateError("Unknown state")


class CoffeeMachine:
    def __init__(self, model: str, maintenanceLimit: int = 200) -> None:
        self.model = model
        self.maintenanceLimit = maintenanceLimit
        self.cyclesAfterMaintenance: int = 0
        self._state: CoffeeMachineState = CoffeeMachineState.IDLE

    def _grind(self) -> None:
        if self._state != "idle":
            raise CoffeeMachinePipelineError(
                "Impossible to start grinding process. Coffee-machine is not ready to use"
            )

        self._state = CoffeeMachineState.GRINDING
        for _ in track(range(0, 100, 20), description="Grinding..."):
            time.sleep(0.5)

    def _brew(self) -> None:
        if self._state != "grinding":
            raise CoffeeMachinePipelineError(
                "Impossible to start brewing process. Coffee beans were not grinded"
            )

        self._state = CoffeeMachineState.BREWING
        for _ in track(range(0, 100, 20), description="Brewing..."):
            time.sleep(0.5)

    def _steam(self) -> None:
        if self._state != "brewing":
            raise CoffeeMachinePipelineError(
                "Impossible to start steaming process. Coffee was not brewed"
            )

        self._state = CoffeeMachineState.STEAMING
        for _ in track(range(0, 100, 20), description="Steaming..."):
            time.sleep(0.5)

    def maintenance(self) -> None:
        match (self._state):
            case "idle":
                print("Maintenance is not needed yet")
            case "maintenance":
                self._state = CoffeeMachineState.IDLE
                self.cyclesAfterMaintenance = 0
            case "grinding" | "brewing" | "steaming":
                raise CoffeeMachineStateError(
                    "Impossible to carry out maintenance during working process"
                )
            case _:
                raise CoffeeMachineStateError("UnknownState")

    def make_coffee(self, coffee: Coffee) -> Coffee:
        if self._state != "idle":
            raise CoffeeMachineStateError("Coffee-machine is not ready to use")
        self._grind()
        self._brew()
        if coffee.with_milk_foam:
            self._steam()

        self._state = CoffeeMachineState.IDLE
        self.cyclesAfterMaintenance += 1
        print("Coffee is made!")
