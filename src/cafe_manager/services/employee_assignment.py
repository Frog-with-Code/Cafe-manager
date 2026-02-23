from uuid import UUID

from cafe_manager.entities.people import Employee
from cafe_manager.common.exceptions import EmployeeError, EmployeeStateError


class EmployeeAssignmentService:
    def __init__(self, employees: list[Employee]) -> None:
        self._employees = employees

    @property
    def employees(self) -> list[Employee]:
        return self._employees[:]

    def assign(self) -> UUID:
        free_employee = next((emp for emp in self._employees if emp.can_work()), None)
        
        if not free_employee:
            raise EmployeeStateError("There is not free employee")
        free_employee.work()
        
        return free_employee.employee_id
    
    def release(self, employee_id: UUID) -> None:
        found_employee = next((emp for emp in self._employees if emp.employee_id == employee_id), None)
        
        if not found_employee:
            raise EmployeeError(f"There is not employee with id: {employee_id}")
        
        found_employee.rest()
