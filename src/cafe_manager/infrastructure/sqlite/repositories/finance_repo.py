from .abstract_repo import *
from cafe_manager.domain.entities.finance import *


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
