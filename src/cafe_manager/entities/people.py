from enum import StrEnum
from cafe_manager.common.exceptions import EmployeeStateError
from uuid import uuid4

class EmployeeState(StrEnum):
    FREE = "free"
    BUSY = "busy"

class Employee:
    def __init__(self, name: str) -> None:
        self.name = name
        self._state = EmployeeState.FREE
        self.employee_id = uuid4()
        
    def can_work(self) -> bool:
        return self._state == EmployeeState.FREE
        
    def work(self) -> None:
        if not self.can_work():
            raise EmployeeStateError("Employee is not free")
        self._state = EmployeeState.BUSY
            
    def rest(self) -> None:
        match(self._state):
            case EmployeeState.FREE:
                print("Employee is already resting")
            case EmployeeState.BUSY:
                self._state = EmployeeState.FREE
                print("Employee is free now")
            case _:
                raise EmployeeStateError("Unknown state")
            
            
class Client:
    def __init__(self, name: str):
        self.client_id = uuid4()
        self.name = name