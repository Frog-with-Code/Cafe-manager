class TableStateError(Exception):
    pass

class TableOccupationError(TableStateError):
    pass

class TableCleaningError(TableStateError):
    pass

class CoffeeMachineStateError(Exception):
    pass

class CoffeeMachinePipelineError(CoffeeMachineStateError):
    pass