import sqlite3
from pathlib import Path
from abc import ABC, abstractmethod
import json
from typing import Any
from datetime import datetime
from uuid import UUID

from cafe_manager.domain.entities.people import Employee, EmployeeState
from cafe_manager.domain.entities.equipment import Table, TableState, ChairState, Chair
from cafe_manager.domain.entities.menu import (
    Ingredient,
    MenuItemCategory,
    Recipe,
    Unit,
    MenuItem,
)
from cafe_manager.domain.entities.finance import (
    Account,
    Money,
    Transaction,
    TransactionType,
)
from cafe_manager.domain.entities.order import Order, OrderState
from tests.test_domain.test_entities.test_menu import ingredient


def adapt_ingredients_dict(d: dict[Ingredient, float]) -> str:
    return json.dumps(
        [
            (ingredient.name, str(ingredient.unit), amount)
            for ingredient, amount in d.items()
        ]
    )


def convert_ingredients_dict(d: str) -> dict[Ingredient, float]:
    return {
        Ingredient(name, unit): float(amount)
        for name, unit, amount in json.loads(d)
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


class SQLiteEmployeeRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    state TEXT,
                    rest_start DATETIME
                )
            """
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row) -> Employee:
        return Employee(
            employee_id=row["id"],
            name=row["name"],
            state=EmployeeState(row["state"]),
            rest_start=row["rest_start"],
        )

    def get_most_free(self) -> Employee | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM employees WHERE state = 'free' ORDER BY rest_start ASC"
            ).fetchone()

            if not row:
                return None

            return self._convert_to_entity(row)

    def get_by_id(self, employee_id: str) -> Employee | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM employees WHERE id = ?",
                (employee_id,),
            ).fetchone()

            if not row:
                return None

            return self._convert_to_entity(row)

    def save(self, employee: Employee) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO employees (id, name, state, rest_start) 
                VALUES(?, ?, ?, ?) 
                ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                state = excluded.state,
                rest_start = excluded.rest_start
                """,
                (
                    employee.employee_id,
                    employee.name,
                    str(employee._state),
                    employee.rest_start,
                ),
            )
            conn.commit()


class SQLiteTableRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                max_places INTEGER, 
                state TEXT, 
                chairs_ids "SET"
                )
            """
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row):
        return Table(
            table_id=row["id"],
            max_places=row["max_places"],
            state=TableState(row["state"]),
            chairs_ids=row["chairs_ids"],
        )

    def get_all(self) -> list[Table] | None:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * from tables").fetchall()

            if not rows:
                return None

            tables = [self._convert_to_entity(row) for row in rows]
            return tables

    def get_by_id(self, table_id: int) -> Table | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * from tables WHERE id = ?", (table_id,)
            ).fetchone()

            if not row:
                return None

            return self._convert_to_entity(row)

    def save(self, table: Table) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO tables (id, max_places, state, chairs_ids) 
                VALUES(?, ?, ?, ?) 
                ON CONFLICT(id) DO UPDATE SET
                max_places = excluded.max_places,
                state = excluded.state,
                chairs_ids = excluded.chairs_ids
                """,
                (table.table_id, table.max_places, str(table._state), table.chairs_ids),
            )
            conn.commit()

    def save_many(self, tables: list[Table]) -> None:
        with self._get_connection() as conn:
            try:
                params = [
                    (table.max_places, str(table._state), table.chairs_ids)
                    for table in tables
                ]

                conn.executemany(
                    """
                    INSERT INTO tables (max_places, state, chairs_ids) 
                    VALUES(?, ?, ?) 
                    ON CONFLICT(id) DO UPDATE SET
                    max_places = excluded.max_places,
                    state = excluded.state,
                    chairs_ids = excluded.chairs_ids
                """,
                    (params),
                )
                conn.commit()
            except:
                conn.rollback()
                raise


class SQLiteChairRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS chairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_id INTEGER,
                    state TEXT
                    )
                """
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row) -> Chair:
        return Chair(
            chair_id=row["id"], table_id=row["table_id"], state=ChairState(row["state"])
        )

    def get_free(self) -> list[Chair] | None:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                    SELECT * from chairs WHERE state = 'available'
                """
            ).fetchall()

            if not rows:
                return None

            chairs = [self._convert_to_entity(row) for row in rows]
            return chairs

    def get_occupied_by_table_id(self, table_id: int) -> list[Chair] | None:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                        SELECT * from chairs WHERE state = 'occupied' AND table_id = ?
                    """,
                (table_id,),
            ).fetchall()

            if not rows:
                return None

            chairs = [self._convert_to_entity(row) for row in rows]
            return chairs

    def save(self, chair: Chair) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO chairs (id, table_id, state) 
                VALUES(?, ?, ?) 
                ON CONFLICT(id) DO UPDATE SET
                table_id = excluded.table_id,
                state = excluded.state
                """,
                (chair.chair_id, chair._table_id, str(chair._state)),
            )
            conn.commit()


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


class SQLiteFinanceRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS balances (
                    account_id UUID PRIMARY KEY,
                    balance MONEY
                );
                
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id UUID PRIMARY KEY,
                    account_id UUID,
                    transaction_type TEXT,
                    money MONEY,
                    description TEXT,
                    time DATETIME
                );
                """
            )

    def _convert_to_entity(self, row: sqlite3.Row) -> Transaction:
        return Transaction(
            transaction_id=row["transaction_id"],
            transaction_type=TransactionType(row["transaction_type"]),
            money=row["money"],
            description=row["description"],
            time=row["time"],
        )

    def get_by_id(self, account_id: UUID) -> Account | None:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                    SELECT b.account_id, b.balance, t.*
                    FROM balances AS b
                    LEFT JOIN transactions AS t
                    USING(account_id)
                    WHERE b.account_id = ?
                    """,
                (account_id,),
            ).fetchall()

            if not rows:
                return None

            balance = rows[0]["balance"]

            transactions = []
            for row in rows:
                if row["transaction_id"]:
                    transactions.append(self._convert_to_entity(row))

            return Account(account_id, balance, transactions)

    def save(self, account: Account) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                    INSERT INTO balances (account_id, balance) 
                    VALUES(?, ?) 
                    ON CONFLICT(account_id) DO UPDATE SET
                    balance = excluded.balance
                """,
                (account.account_id, account.balance),
            )

            if account.history:
                params = [
                    (
                        account.account_id,
                        t.transaction_id,
                        str(t.transaction_type),
                        t.money,
                        t.description,
                        t.time,
                    )
                    for t in account.history
                ]
                conn.executemany(
                    f"""
                        INSERT INTO transactions (account_id, transaction_id, transaction_type, money, description, time) 
                        VALUES(?, ?, ?, ?, ?, ?)
                        ON CONFLICT(transaction_id) DO NOTHING
                    """,
                    (params),
                )
            conn.commit()


class SQLiteOrderRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    client_id TEXT,
                    table_id INTEGER,
                    items TEXT,     
                    created_at DATETIME, 
                    paid_at TEXT,
                    total_price MONEY, 
                    state TEXT   
                )
                """
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row) -> Any:
        items_dict = self._deserialize_items(row["items"])

        return Order(
            order_id=row["id"],
            client_id=row["client_id"],
            table_id=row["table_id"],
            items=items_dict,
            created_at=row["created_at"],
            paid_at=row["paid_at"],
            total_price=row["total_price"],
            state=OrderState(row["state"]),
        )

    def _serialize_items(self, items: dict[MenuItem, int]) -> str:
        data = []
        for item, amount in items.items():
            data.append(
                {
                    "name": str(item.name),
                    "requires_milk_foam": str(item.recipe.requires_milk_foam),
                    "ingredients": adapt_ingredients_dict(item.recipe.ingredients),
                    "price": str(item.price.amount),
                    "category": str(item.category),
                    "amount": amount,
                }
            )
        return json.dumps(data)

    def _deserialize_items(self, json_string: str) -> dict[MenuItem, int]:
        if not json_string:
            return {}

        data = json.loads(json_string)
        items = {}
        for d in data:
            i = MenuItem(
                name=d["name"],
                recipe=Recipe(
                    d["requires_milk_foam"] == "True",
                    convert_ingredients_dict(d["ingredients"]),
                ),
                price=Money.from_any(d["price"]),
                category=MenuItemCategory(d["category"]),
            )
            items[i] = int(d["amount"])

        return items

    def get_by_id(self, order_id: str) -> Order | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * from orders WHERE id = ?", (order_id,)
            ).fetchone()

            if not row:
                return None

            return self._convert_to_entity(row)

    def get_oldest_paid(self) -> Order | None:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * from orders WHERE state = 'paid' ORDER BY paid_at ASC"
            ).fetchone()

            if not row:
                return None

            return self._convert_to_entity(row)

    def get_paid_from_oldest(self) -> list[Order] | None:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * from orders WHERE state = 'paid' ORDER BY paid_at ASC"
            ).fetchall()

            if not rows:
                return None

            orders = [self._convert_to_entity(row) for row in rows]
            return orders

    def save(self, order: Order) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                    INSERT INTO orders (id, client_id, table_id, items, created_at, paid_at, total_price, state) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?) 
                    ON CONFLICT(id) DO UPDATE SET
                    items = excluded.items,       
                    paid_at = excluded.paid_at,    
                    total_price = excluded.total_price, 
                    state = excluded.state
                """,
                (
                    order.order_id,
                    order.client_id,
                    order.table_id,
                    self._serialize_items(order.items),
                    order.created_at,
                    order.paid_at,
                    order.total_price,
                    str(order._state),
                ),
            )
            conn.commit()


class SQLiteMenuRepo(AbstractSQliteRepo):
    def __init__(self, db_path: Path | str):
        super().__init__(db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS menu (
                    name TEXT PRIMARY KEY,
                    requires_milk_foam TEXT,
                    ingredients INGR_DICT,
                    price MONEY,
                    category TEXT
                )"""
            )
            conn.commit()

    def _convert_to_entity(self, row: sqlite3.Row) -> MenuItem:
        return MenuItem(
            name=row["name"],
            recipe=Recipe(
                row["requires_milk_foam"] == "True",
                convert_ingredients_dict(row["ingredients"]),
            ),
            price=row["price"],
            category=MenuItemCategory(row["category"]),
        )

    def get_by_names(self, names: set[str]) -> list[MenuItem] | None:
        with self._get_connection() as conn:
            placeholders = ", ".join(["?"] * len(names))
            rows = conn.execute(
                f"SELECT * from menu WHERE name IN ({placeholders})",
                tuple(names),
            ).fetchall()

            if not rows:
                return None

            items = [self._convert_to_entity(row) for row in rows]
            return items

    def save(self, item: MenuItem) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                    INSERT INTO menu (name, requires_milk_foam, ingredients, price, category)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                    requires_milk_foam = excluded.requires_milk_foam,
                    ingredients = excluded.ingredients,
                    price = excluded.price,
                    category = excluded.category
                """,
                (
                    item.name,
                    str(item.recipe.requires_milk_foam),
                    adapt_ingredients_dict(item.recipe.ingredients),
                    item.price,
                    str(item.category),
                ),
            )
