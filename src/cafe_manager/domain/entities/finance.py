from __future__ import annotations
from dataclasses import dataclass, field, replace
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from enum import StrEnum
from datetime import datetime
from uuid import uuid4, UUID

from cafe_manager.common.exceptions import IncorrectMoneyAmountError
from cafe_manager.common.utils import validate_non_negative


@dataclass(frozen=True)
class Money:
    amount: Decimal = Decimal("0.00")

    @classmethod
    def from_any(cls, amount: Decimal | int | float | str) -> "Money":
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except:
                raise IncorrectMoneyAmountError(
                    f"Impossible to convert {amount} to Decimal"
                )

        return cls(amount)

    def __post_init__(self) -> None:
        validate_non_negative(self.amount)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount <= other.amount

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount >= other.amount

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount + other.amount)

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(self.amount - other.amount)

    def __mul__(self, factor: int | Decimal | float) -> "Money":
        return self._multiply_by_scalar(factor)

    def __rmul__(self, factor: int | Decimal | float) -> "Money":
        return self._multiply_by_scalar(factor)

    def _multiply_by_scalar(self, factor: int | Decimal | float) -> "Money":
        validate_non_negative(factor)

        if isinstance(factor, float):
            factor = Decimal(str(factor))

        return Money(self.amount * factor)

    def __truediv__(self, divisor: int | Decimal | float) -> "Money":
        validate_non_negative(divisor)

        if isinstance(divisor, float):
            divisor = Decimal(str(divisor))

        if divisor == 0:
            raise ZeroDivisionError("Cannot divide money by zero")

        raw_amount = self.amount / divisor
        return Money(raw_amount.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))

    def __str__(self) -> str:
        return f"{self.amount:.2f} BYN"


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass(frozen=True)
class Transaction:
    transaction_type: TransactionType
    amount: Money
    description: str = ""
    transaction_id: UUID = field(default_factory=uuid4)
    time: datetime = field(default_factory=datetime.now)
