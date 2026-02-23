from uuid import UUID
from cafe_manager.common.exceptions import TableOccupationError, TableError
from cafe_manager.entities.equipment import Table


class TableReservingService:
    def __init__(self, tables: list[Table]) -> None:
        self._tables = tables

    @property
    def tables(self) -> list[Table]:
        return self._tables[:]

    def reserve(self, people_amount: int) -> UUID:
        candidates = [t for t in self._tables if t.can_be_occupied(people_amount)]

        if not candidates:
            raise TableOccupationError(
                f"There is not available table for {people_amount} people"
            )

        best_table = min(candidates, key=lambda table: table.place_amount)
        best_table.occupy(people_amount)

        return best_table.table_id

    def free(self, table_id: UUID) -> None:
        found_table = next((t for t in self._tables if t.table_id == table_id), None)

        if not found_table:
            raise TableError(f"There is not table with id: {table_id}")
        
        found_table.free()
