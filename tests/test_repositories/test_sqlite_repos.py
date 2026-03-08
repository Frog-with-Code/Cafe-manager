import pytest
from uuid import uuid4
from datetime import datetime
from dataclasses import replace

from cafe_manager.repositories.sqlite_repos import *
from tests.test_domain.test_entities.test_menu import recipe


class TestSQLiteEmployeeRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe.db"
        repository = SQLiteEmployeeRepo(db_file)
        return repository

    @pytest.fixture
    def sample_employee(self):
        emp = Employee(
            employee_id="abc",
            name="Artem",
            state=EmployeeState("busy"),
            rest_start=datetime.now(),
        )
        return emp

    def test_init_db_creates_table(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
            )
            table_exists = cursor.fetchone()
            assert table_exists is not None

    def test_save_and_get_by_id(self, repo, sample_employee):
        repo.save(sample_employee)

        fetched_emp = repo.get_by_id("abc")

        assert fetched_emp is not None
        assert fetched_emp.employee_id == "abc"
        assert fetched_emp.name == "Artem"
        assert fetched_emp._state == EmployeeState("busy")
        assert fetched_emp.rest_start == sample_employee.rest_start

    def test_get_by_id_not_found(self, repo):
        assert repo.get_by_id("not-exists") is None

    def test_save_updates_existing_employee(self, repo, sample_employee):
        repo.save(sample_employee)

        sample_employee.name = "Artem Updated"
        sample_employee._state = EmployeeState("free")

        repo.save(sample_employee)

        fetched_emp = repo.get_by_id("abc")
        assert fetched_emp is not None
        assert fetched_emp.name == "Artem Updated"
        assert fetched_emp._state == EmployeeState("free")

        with repo._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            assert count == 1

    def test_get_most_free_empty_db(self, repo):
        assert repo.get_most_free() is None

    def test_get_most_free_no_free_employees(self, repo, sample_employee):
        sample_employee._state = EmployeeState("busy")
        repo.save(sample_employee)

        assert repo.get_most_free() is None

    def test_get_most_free_logic(self, repo):
        emp1 = Employee(
            employee_id="1",
            name="Employee 1",
            state=EmployeeState("free"),
            rest_start=datetime.fromisoformat("2023-01-01T15:00:00"),
        )
        emp1._state = EmployeeState("free")

        emp2 = Employee(
            employee_id="2",
            name="Employee 2",
            state=EmployeeState("free"),
            rest_start=datetime.fromisoformat("2023-01-01T10:00:00"),
        )
        emp2._state = EmployeeState("free")

        emp3 = Employee(
            employee_id="3",
            name="Employee 3",
            state=EmployeeState("busy"),
            rest_start=datetime.fromisoformat("2022-01-01T01:00:00"),
        )
        emp3._state = EmployeeState("busy")

        repo.save(emp1)
        repo.save(emp2)
        repo.save(emp3)

        most_free = repo.get_most_free()

        assert most_free is not None
        assert most_free.employee_id == "2"
        assert most_free.name == "Employee 2"


class TestSQLiteTableRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_tables.db"
        repository = SQLiteTableRepo(db_file)
        return repository

    @pytest.fixture
    def sample_table(self):
        t = Table(
            table_id=1,
            max_places=4,
            state=TableState("available"),
            chairs_ids={101, 102, 103, 104},
        )
        return t

    def test_init_db_creates_table(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tables'"
            )
            assert cursor.fetchone() is not None

    def test_save_and_get_by_id(self, repo, sample_table):
        repo.save(sample_table)

        fetched_table = repo.get_by_id(1)

        assert fetched_table is not None
        assert fetched_table.table_id == 1
        assert fetched_table.max_places == 4
        assert fetched_table._state == TableState("available")
        assert fetched_table.chairs_ids == {101, 102, 103, 104}
        assert isinstance(fetched_table.chairs_ids, set)

    def test_get_by_id_not_found(self, repo):
        assert repo.get_by_id(99) is None

    def test_get_all_empty_db(self, repo):
        assert repo.get_all() is None

    def test_save_updates_existing_table(self, repo, sample_table):
        repo.save(sample_table)

        sample_table._state = TableState("occupied")
        sample_table._chairs_ids = {101, 102, 103}

        repo.save(sample_table)

        fetched = repo.get_by_id(1)
        assert fetched._state == TableState("occupied")
        assert fetched.chairs_ids == {101, 102, 103}

        with repo._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM tables").fetchone()[0]
            assert count == 1

    def test_save_many_and_get_all(self, repo):
        table1 = Table(
            table_id=1, max_places=2, state=TableState("available"), chairs_ids={10, 11}
        )
        table2 = Table(
            table_id=2,
            max_places=6,
            state=TableState("occupied"),
            chairs_ids={20, 21, 22, 23, 24, 25},
        )
        table3 = Table(
            table_id=3, max_places=4, state=TableState("dirty"), chairs_ids={30, 31}
        )

        repo.save_many([table1, table2, table3])

        all_tables = repo.get_all()

        assert len(all_tables) == 3

        ids = {t.table_id for t in all_tables}
        assert ids == {1, 2, 3}


class TestSQLiteChairRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_chairs.db"
        repository = SQLiteChairRepo(db_file)
        return repository

    def test_init_db_creates_table(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chairs'"
            )
            assert cursor.fetchone() is not None

    def test_save_and_update_chair(self, repo):
        chair = Chair(chair_id=1, table_id=10, state=ChairState("available"))

        repo.save(chair)

        chair._state = ChairState("occupied")
        chair._table_id = 12
        repo.save(chair)

        with repo._get_connection() as conn:
            rows = conn.execute("SELECT * FROM chairs WHERE id = 1").fetchall()

            assert len(rows) == 1
            assert rows[0]["state"] == "occupied"
            assert rows[0]["table_id"] == 12

    def test_get_free_empty_db(self, repo):
        assert repo.get_free() is None

    def test_get_free_logic(self, repo):
        c1 = Chair(chair_id=1, table_id=10, state=ChairState("available"))
        c2 = Chair(chair_id=2, table_id=10, state=ChairState("occupied"))
        c3 = Chair(chair_id=3, table_id=11, state=ChairState("available"))

        repo.save(c1)
        repo.save(c2)
        repo.save(c3)

        free_chairs = repo.get_free()

        assert free_chairs is not None
        assert len(free_chairs) == 2

        free_ids = {c.chair_id for c in free_chairs}
        assert free_ids == {1, 3}

    def test_get_occupied_by_table_id_empty(self, repo):
        assert repo.get_occupied_by_table_id(999) is None

    def test_get_occupied_by_table_id_logic(self, repo):
        c1 = Chair(chair_id=1, table_id=10, state=ChairState("occupied"))
        c2 = Chair(chair_id=2, table_id=10, state=ChairState("available"))
        c3 = Chair(chair_id=3, table_id=11, state=ChairState("occupied"))

        repo.save(c1)
        repo.save(c2)
        repo.save(c3)

        occupied_chairs = repo.get_occupied_by_table_id(10)

        assert occupied_chairs is not None
        assert len(occupied_chairs) == 1
        assert occupied_chairs[0].chair_id == 1
        assert occupied_chairs[0]._table_id == 10
        assert occupied_chairs[0]._state == ChairState("occupied")


class TestSQLiteInventoryRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_inventory.db"
        repository = SQLiteInventoryRepo(db_file)
        return repository

    @pytest.fixture
    def sample_inventory(self):
        return {
            Ingredient("Coffee Beans", Unit("g")): 1500.0,
            Ingredient("Milk", Unit("ml")): 2000.0,
            Ingredient("Sugar", Unit("g")): 500.0,
        }

    def test_init_db_creates_table(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'"
            )
            assert cursor.fetchone() is not None

    def test_save_many_and_get_by_names(self, repo, sample_inventory):
        repo.save_many(sample_inventory)

        names_to_fetch = {"Coffee Beans", "Sugar"}
        fetched_inventory = repo.get_by_names(names_to_fetch)

        assert fetched_inventory is not None
        assert len(fetched_inventory) == 2

        coffee = Ingredient("Coffee Beans", Unit("g"))
        sugar = Ingredient("Sugar", Unit("g"))

        assert coffee in fetched_inventory
        assert fetched_inventory[coffee] == 1500.0

        assert sugar in fetched_inventory
        assert fetched_inventory[sugar] == 500.0

    def test_get_by_names_not_found(self, repo, sample_inventory):
        repo.save_many(sample_inventory)

        assert repo.get_by_names({"Water", "Tea"}) is None

    def test_get_by_names_empty_set(self, repo):
        assert repo.get_by_names(set()) is None

    def test_save_many_updates_existing_items(self, repo, sample_inventory):
        repo.save_many(sample_inventory)

        updated_inventory = {
            Ingredient("Coffee Beans", Unit("g")): 3000.0,
            Ingredient("Milk", Unit("ml")): 5000.0,
        }
        repo.save_many(updated_inventory)

        fetched = repo.get_by_names({"Coffee Beans", "Milk", "Sugar"})

        coffee = Ingredient("Coffee Beans", Unit("g"))
        milk = Ingredient("Milk", Unit("ml"))
        sugar = Ingredient("Sugar", Unit("g"))

        assert fetched[coffee] == 3000.0
        assert fetched[milk] == 5000.0
        assert fetched[sugar] == 500.0

        with repo._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
            assert count == 3


class TestSQLiteFinanceRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_finance.db"
        repository = SQLiteFinanceRepo(db_file)
        return repository

    @pytest.fixture
    def sample_account(self):
        acc_id = uuid4()

        t1 = Transaction(
            transaction_id=uuid4(),
            transaction_type=TransactionType("income"),
            money=Money.from_any(1000.50),
            description="Order paying",
            time=datetime(2023, 10, 1, 14, 30),
        )
        t2 = Transaction(
            transaction_id=uuid4(),
            transaction_type=TransactionType("expense"),
            money=Money.from_any(200.00),
            description="Milk buying",
            time=datetime(2023, 10, 2, 9, 15),
        )

        account = Account(
            account_id=acc_id, balance=Money.from_any(800.50), history=[t1, t2]
        )
        return account

    def test_init_db_creates_tables(self, repo):
        with repo._get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('balances', 'transactions')"
            ).fetchall()
            names = {row["name"] for row in tables}
            assert "balances" in names
            assert "transactions" in names

    def test_save_and_get_by_id(self, repo, sample_account):
        repo.save(sample_account)

        fetched_account = repo.get_by_id(sample_account.account_id)

        assert fetched_account is not None
        assert fetched_account.account_id == sample_account.account_id
        assert fetched_account.balance == Money.from_any(800.50)

        assert len(fetched_account.history) == 2

        expected_tx_ids = {t.transaction_id for t in sample_account.history}
        fetched_tx_ids = {t.transaction_id for t in fetched_account.history}
        assert expected_tx_ids == fetched_tx_ids

    def test_get_by_id_not_found(self, repo):
        assert repo.get_by_id(uuid4()) is None

    def test_save_account_with_empty_history(self, repo):
        acc_id = uuid4()
        empty_acc = Account(
            account_id=acc_id, balance=Money.from_any(5000.0), history=[]
        )

        repo.save(empty_acc)

        fetched = repo.get_by_id(acc_id)
        assert fetched is not None
        assert fetched.balance == Money.from_any(5000.0)
        assert len(fetched.history) == 0

    def test_update_account_add_transaction(self, repo, sample_account):
        repo.save(sample_account)

        new_tx = Transaction(
            transaction_id=uuid4(),
            transaction_type=TransactionType("income"),
            money=Money.from_any(300.00),
            description="Tips",
            time=datetime.now(),
        )
        sample_account._history.append(new_tx)
        sample_account._balance = Money.from_any(1100.50)

        repo.save(sample_account)

        fetched = repo.get_by_id(sample_account.account_id)

        assert fetched.balance == Money.from_any(1100.50)
        assert len(fetched.history) == 3

        with repo._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            assert count == 3


class TestSQLiteOrderRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_orders.db"
        repository = SQLiteOrderRepo(db_file)
        return repository

    @pytest.fixture
    def sample_item(self):
        recipe = Recipe(
            requires_milk_foam=True,
            ingredients={
                Ingredient("Coffee", Unit("g")): 10.0,
                Ingredient("Milk", Unit("ml")): 150.0,
            },
        )
        return MenuItem(
            name="Latte",
            recipe=recipe,
            price=Money.from_any(350.0),
            category=MenuItemCategory("coffee"),
        )

    @pytest.fixture
    def sample_order(self, sample_item):
        order = Order(
            order_id="ord-123",
            client_id="cli-555",
            table_id=1,
            items={sample_item: 2},
            created_at=datetime(2023, 10, 1, 10, 0, 0),
            paid_at=None,
            total_price=Money.from_any(700.0),
            state=OrderState("awaiting-payment"),
        )
        return order

    def test_init_db(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
            )
            assert cursor.fetchone() is not None

    def test_save_and_get_by_id(self, repo, sample_order, sample_item):
        repo.save(sample_order)

        fetched_order = repo.get_by_id("ord-123")

        assert fetched_order is not None
        assert fetched_order.order_id == "ord-123"
        assert fetched_order.client_id == "cli-555"
        assert fetched_order.table_id == 1
        assert fetched_order._state == OrderState("awaiting-payment")

        assert fetched_order.total_price == Money.from_any(700.0)

        assert isinstance(fetched_order.created_at, datetime)
        assert (
            fetched_order.created_at.isoformat() == sample_order.created_at.isoformat()
        )

        assert len(fetched_order.items) == 1
        fetched_item = list(fetched_order.items.keys())[0]
        assert fetched_item.name == "Latte"
        assert fetched_item.category == MenuItemCategory("coffee")
        assert fetched_item.recipe.requires_milk_foam is True

        ingrs = fetched_item.recipe.ingredients
        coffee = Ingredient("Coffee", Unit("g"))
        assert coffee in ingrs
        assert ingrs[coffee] == 10.0

    def test_get_oldest_paid(self, repo):
        o1 = Order(
            order_id="1",
            client_id="c",
            table_id=2,
            items={},
            created_at=datetime.fromisoformat("2022-10-01T10:00:00"),
            paid_at=None,
            total_price=Money.from_any(0),
            state=OrderState("awaiting-payment"),
        )

        o2 = Order(
            order_id="2",
            client_id="c",
            table_id=2,
            items={},
            created_at=datetime.now(),
            paid_at=datetime.fromisoformat("2023-10-01T10:00:00"),
            total_price=Money.from_any(0),
            state=OrderState("paid"),
        )

        o3 = Order(
            order_id="3",
            client_id="c",
            table_id=2,
            items={},
            created_at=datetime.now(),
            paid_at=datetime.fromisoformat("2023-10-02T10:00:00"),
            total_price=Money.from_any(0),
            state=OrderState("paid"),
        )

        repo.save(o1)
        repo.save(o2)
        repo.save(o3)

        oldest = repo.get_oldest_paid()

        assert oldest is not None
        assert oldest.order_id == "2"

    def test_get_paid_from_oldest(self, repo):
        o1 = Order(
            order_id="new",
            client_id="c",
            table_id=2,
            items={},
            created_at=datetime.now(),
            paid_at=datetime.fromisoformat("2025-01-01T15:00:00"),
            total_price=Money.from_any(0),
            state=OrderState("paid"),
        )

        o2 = Order(
            order_id="old",
            client_id="c",
            table_id=2,
            items={},
            created_at=datetime.now(),
            paid_at=datetime.fromisoformat("2023-01-02T15:00:00"),
            total_price=Money.from_any(0),
            state=OrderState("paid"),
        )

        repo.save(o1)
        repo.save(o2)

        orders = repo.get_paid_from_oldest()

        assert orders is not None
        assert len(orders) == 2
        assert orders[0].order_id == "old"
        assert orders[1].order_id == "new"

    def test_save_update_status(self, repo, sample_order):
        repo.save(sample_order)

        sample_order._state = OrderState("paid")
        sample_order.paid_at = datetime.now()

        repo.save(sample_order)

        fetched_order = repo.get_by_id(sample_order.order_id)
        assert fetched_order._state == OrderState("paid")
        assert fetched_order.paid_at is not None


class TestSQLiteMenuRepo:
    @pytest.fixture
    def repo(self, tmp_path):
        db_file = tmp_path / "test_cafe_menu.db"
        repository = SQLiteMenuRepo(db_file)
        return repository

    @pytest.fixture
    def sample_item(self):
        recipe = Recipe(
            requires_milk_foam=True,
            ingredients={
                Ingredient("Coffee", Unit("g")): 18.0,
                Ingredient("Water", Unit("ml")): 30.0,
            },
        )
        return MenuItem(
            name="Espresso",
            recipe=recipe,
            price=Money.from_any(150.0),
            category=MenuItemCategory("coffee"),
        )

    def test_init_db(self, repo):
        with repo._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='menu'"
            )
            assert cursor.fetchone() is not None

    def test_save_and_get_by_names(self, repo, sample_item):
        repo.save(sample_item)

        fetched_items = repo.get_by_names({"Espresso"})

        assert len(fetched_items) == 1

        item = fetched_items[0]
        assert item.name == "Espresso"
        assert item.category == MenuItemCategory("coffee")

        assert item.price == Money.from_any(150.0)

        assert item.recipe.requires_milk_foam is True
        assert len(item.recipe.ingredients) == 2

        coffee = Ingredient("Coffee", Unit("g"))
        assert coffee in item.recipe.ingredients
        assert item.recipe.ingredients[coffee] == 18.0

    def test_get_by_names_multiple(self, repo):
        i1 = MenuItem(
            "Tea", Recipe(False, {}), Money.from_any(50), MenuItemCategory("tea")
        )
        i2 = MenuItem(
            "Cake", Recipe(False, {}), Money.from_any(200), MenuItemCategory("bakery")
        )
        i3 = MenuItem(
            "Latte", Recipe(True, {}), Money.from_any(300), MenuItemCategory("coffee")
        )

        repo.save(i1)
        repo.save(i2)
        repo.save(i3)

        items = repo.get_by_names({"Tea", "Latte"})

        assert items is not None
        assert len(items) == 2
        names = {i.name for i in items}
        assert names == {"Tea", "Latte"}

    def test_get_by_names_partial_missing(self, repo, sample_item):
        repo.save(sample_item)

        items = repo.get_by_names({"Espresso", "Unicorn"})

        assert items is not None
        assert len(items) == 1
        assert items[0].name == "Espresso"

    def test_get_by_names_none_found(self, repo):
        assert repo.get_by_names({"Nothing"}) is None

    def test_update_item_price(self, repo, sample_item):
        repo.save(sample_item)

        sample_item = replace(
            sample_item, price=Money.from_any(180.0), category=MenuItemCategory.COCKTAIL
        )

        repo.save(sample_item)

        items = repo.get_by_names({"Espresso"})
        updated_item = items[0]

        assert updated_item.price.amount == 180.0
        assert updated_item.category == MenuItemCategory.COCKTAIL

        with repo._get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM menu").fetchone()[0]
            assert count == 1
