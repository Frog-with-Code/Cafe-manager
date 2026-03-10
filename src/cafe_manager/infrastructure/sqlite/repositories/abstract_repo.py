import sqlite3
import json
from datetime import datetime
from uuid import UUID
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from cafe_manager.domain.entities.menu import Ingredient
from cafe_manager.domain.entities.finance import Money


def adapt_ingredients_dict(d: dict[Ingredient, float]) -> str:
    return json.dumps(
        [
            (ingredient.name, str(ingredient.unit), amount)
            for ingredient, amount in d.items()
        ]
    )


def convert_ingredients_dict(d: str) -> dict[Ingredient, float]:
    return {
        Ingredient(name, unit): float(amount) for name, unit, amount in json.loads(d)
    }


sqlite3.register_adapter(set, lambda s: json.dumps(list(s)))
sqlite3.register_converter("SET", lambda s: set(json.loads(s.decode())))

sqlite3.register_adapter(datetime, lambda d: d.isoformat())
sqlite3.register_converter("DATETIME", lambda d: datetime.fromisoformat(d.decode()))

sqlite3.register_adapter(Money, lambda m: str(m.amount))
sqlite3.register_converter("MONEY", lambda m: Money.from_any(m.decode()))

sqlite3.register_adapter(UUID, lambda u: str(u))
sqlite3.register_converter("UUID", lambda u: UUID(u.decode()))


class AbstractSQliteRepo(ABC):
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    @abstractmethod
    def _init_db(self) -> None: ...

    @abstractmethod
    def _convert_to_entity(self, row: sqlite3.Row) -> Any: ...
