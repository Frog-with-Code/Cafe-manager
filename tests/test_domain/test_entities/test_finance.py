import pytest
from decimal import Decimal
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import FrozenInstanceError

from cafe_manager.domain.entities.finance import Money, Transaction, TransactionType
from cafe_manager.common.exceptions import IncorrectMoneyAmountError


class TestMoney:
    def test_create_money(self):
        m = Money(Decimal(100))
        assert m.amount == 100

    def test_create_money_from_correct_types(self):
        from_int = Money.from_any(5)
        from_float = Money.from_any(5.0)
        from_str = Money.from_any("5")

        assert from_int.amount == 5
        assert isinstance(from_int.amount, Decimal) is True
        assert from_float.amount == 5
        assert isinstance(from_float.amount, Decimal) is True
        assert from_str.amount == 5
        assert isinstance(from_str.amount, Decimal) is True

    def test_create_money_from_incorrect_types(self):
        with pytest.raises(IncorrectMoneyAmountError):
            Money.from_any("g")
            Money.from_any([])  # type: ignore
            Money.from_any({})  # type: ignore

    def test_create_money_negative(self):
        with pytest.raises(ValueError):
            Money(Decimal(-10))
        with pytest.raises(ValueError):
            Money.from_any(-10)

    def test_money_equality(self):
        assert Money(Decimal(100)) == Money.from_any(100)
        assert Money(Decimal(100)) != Money(Decimal(200))

    def test_money_comparison(self):
        m1 = Money(Decimal(50))
        m2 = Money(Decimal(100))

        assert m1 < m2
        assert m2 > m1
        assert m1 <= m2
        assert m1 <= Money(Decimal(50))

    def test_money_arithmetic(self):
        m1 = Money(Decimal(100))
        m2 = Money(Decimal(50))

        assert m1 + m2 == Money(Decimal(150))
        assert m1 - m2 == Money(Decimal(50))
        assert m1 * 2 == Money(Decimal(200))
        assert m1 * 0.5 == Money(Decimal(50))


class TestTransaction:
    def test_create_with_required_fields_only(self):
        amount = Money(Decimal("100.50"))
        tx = Transaction(transaction_type=TransactionType.INCOME, amount=amount)

        assert tx.transaction_type == TransactionType.INCOME
        assert tx.amount == amount
        assert tx.description == ""
        assert isinstance(tx.transaction_id, UUID)
        assert isinstance(tx.time, datetime)

    def test_create_with_all_explicit_fields(self):
        custom_uuid = uuid4()
        custom_time = datetime(2023, 10, 25, 12, 0, 0)
        amount = Money(Decimal("50.00"))

        tx = Transaction(
            transaction_type=TransactionType.EXPENSE,
            amount=amount,
            description="Покупка кофе",
            transaction_id=custom_uuid,
            time=custom_time,
        )

        assert tx.transaction_type == TransactionType.EXPENSE
        assert tx.amount == amount
        assert tx.description == "Покупка кофе"
        assert tx.transaction_id == custom_uuid
        assert tx.time == custom_time

    def test_transaction_is_frozen(self):
        tx = Transaction(
            transaction_type=TransactionType.INCOME, amount=Money(Decimal("100"))
        )

        with pytest.raises(FrozenInstanceError):
            tx.description = "Попытка изменить описание"  # type: ignore

        with pytest.raises(FrozenInstanceError):
            tx.amount = Money(Decimal("200"))  # type: ignore

    def test_dynamic_default_factories(self):
        tx1 = Transaction(
            transaction_type=TransactionType.INCOME, amount=Money(Decimal("10"))
        )
        tx2 = Transaction(
            transaction_type=TransactionType.EXPENSE, amount=Money(Decimal("20"))
        )

        assert tx1.transaction_id != tx2.transaction_id

        assert tx1.time is not tx2.time
