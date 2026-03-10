from .abstract_repo import *
from cafe_manager.domain.entities.menu import Ingredient, Unit


class SQLiteInventoryRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS inventory (
                name TEXT PRIMARY KEY,
                unit TEXT,
                amount REAL
                )"""
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row) -> tuple[Ingredient, float]:
        return Ingredient(row["name"], Unit(row["unit"])), row["amount"]

    def get_by_names(self, names: set[str]) -> dict[Ingredient, float] | None:
        with self._get_connection() as conn:
            placeholders = ", ".join(["?"] * len(names))
            rows = conn.execute(
                f"SELECT * from inventory WHERE name IN ({placeholders})", tuple(names)
            ).fetchall()

            if not rows:
                return None

            inventory = dict(self._convert_to_entity(row) for row in rows)
            return inventory

    def save_many(self, inventory: dict[Ingredient, float]) -> None:
        if not inventory:
            return

        with self._get_connection() as conn:
            try:
                params = [
                    (ingredient.name, str(ingredient.unit), amount)
                    for ingredient, amount in inventory.items()
                ]
                conn.executemany(
                    """
                    INSERT INTO inventory (name, unit, amount) 
                    VALUES(?, ?, ?) 
                    ON CONFLICT(name) DO UPDATE SET
                    amount = excluded.amount,
                    unit = excluded.unit
                """,
                    (params),
                )

                conn.commit()
            except:
                conn.rollback()
                raise
