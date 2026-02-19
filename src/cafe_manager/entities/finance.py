from __future__ import annotations
from dataclasses import dataclass, replace, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from enum import StrEnum
from datetime import datetime
from uuid import uuid4, UUID

from cafe_manager.common.utils import validate_non_negative
from cafe_manager.common.exceptions import DifferentCurrenciesError, InsufficientBudgetError


class Currency(StrEnum):
    """
    Supported currencies for financial operations.

    Values:
        USD: United States Dollar.
        EUR: Euro.
        BYN: Belarusian Ruble.
    """

    USD = "USD"
    EUR = "EUR"
    BYN = "BYN"


@dataclass(frozen=True)
class Money:
    """
    Immutable representation of a monetary amount in a specific currency.

    This class supports basic arithmetic operations (+, -, *, /) and comparison
    operators. Operations between Money instances require them to be in the
    same currency.

    Attributes:
        amount (Decimal): The numeric value of the money (must be non-negative).
        currency (Currency): The currency type associated with the amount.
    """

    amount: Decimal = 0
    currency: Currency = Currency("USD")

    def validate_currency(self, other: Money) -> None:
        """
        Ensure that another Money instance has the same currency as this one.

        Args:
            other (Money): The money object to check.

        Raises:
            DifferentCurrenciesError: If the currencies do not match.
        """
        if self.currency != other.currency:
            raise DifferentCurrenciesError(
                f"This operation with different currencies ({self.currency} and {other.currency}) is impossible!"
            )

    def __eq__(self, other: Money) -> bool:
        """Check equality based on amount and currency."""
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: Money) -> bool:
        """Check if amount is strictly less than other (same currency required)."""
        self.validate_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        """Check if amount is less than or equal to other (same currency required)."""
        self.validate_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        """Check if amount is strictly greater than other (same currency required)."""
        self.validate_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        """Check if amount is greater than or equal to other (same currency required)."""
        self.validate_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        """Return string representation (e.g., '100.50 USD')."""
        return f"{self.amount} {self.currency}"

    def __add__(self, other: Money) -> Money:
        """
        Add two Money instances.

        Returns:
            Money: A new instance with the summed amount.
        """
        self.validate_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        """
        Subtract two Money instances.

        Returns:
            Money: A new instance with the subtracted amount.
        """
        self.validate_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int | float | Decimal) -> Money:
        """
        Multiply the monetary amount by a numeric factor.

        Args:
            factor (int | float | Decimal): The multiplier (must be non-negative).

        Returns:
            Money: A new instance with the scaled amount.
        """
        validate_non_negative(factor)
        return Money(self.amount * factor, self.currency)

    def __truediv__(self, factor: int | float | Decimal) -> Money:
        """
        Divide the monetary amount by a numeric factor.

        Results are rounded to 5 decimal places using ROUND_HALF_UP.

        Args:
            factor (int | float | Decimal): The divisor (must be non-negative).

        Returns:
            Money: A new instance with the divided amount.
        """
        validate_non_negative(factor)
        raw_amount = self.amount / factor
        return Money(
            raw_amount.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP),
            self.currency,
        )

    def __post_init__(self) -> None:
        """Validate that the amount is non-negative after initialization."""
        validate_non_negative(self.amount)


class TransactionType(StrEnum):
    """
    Categorization of financial operations.

    Values:
    """

    INCOME = "income"
    EXPENSE = "expense"


@dataclass(frozen=True)
class Transaction:
    """
    Immutable record of a financial operation.

    Stores all relevant details about a movement of money, including the source,
    destination, amounts involved (in both source and target currencies), and metadata.
    Validates logical consistency of fields based on the transaction type upon initialization.

    Attributes:
        transaction_type (TransactionType): The category of the operation.
        source_company (Optional[AbstractCompany]): The entity sending funds (required for TRANSFER).
        target_company (Optional[AbstractCompany]): The entity receiving funds (required for TRANSFER/DEPOSIT).
        description (str): Human-readable note or reference.
        transaction_id (UUID): Unique identifier for the transaction (auto-generated).
        status (TransactionStatus): Result of the operation. Defaults to PENDING.
        time (datetime): Timestamp of creation (auto-generated).
    """

    transaction_type: TransactionType
    amount: Money
    description: str = ""
    transaction_id: UUID = field(default_factory=uuid4)
    time: datetime = field(default_factory=datetime.now)


class CurrencyService:
    """
    Service for handling currency exchange rates and conversions.

    Attributes:
        _rates (dict[Currency, Decimal]): Dictionary mapping currencies to their
            values relative to a base currency (usually USD).
        _creation_date (datetime): Timestamp of when the service (and its rates) was initialized.
    """

    def __init__(self, rates: dict[Currency, Decimal]) -> None:
        """
        Initialize the service with specific exchange rates.

        Args:
            rates (dict[Currency, Decimal]): A map of Currency to exchange rate.
        """
        self._rates = rates
        self._creation_date = datetime.now()

    def convert(self, money: Money, target_currency: Currency) -> Money:
        """
        Convert a Money object to a target currency using stored rates.

        Formula: New Amount = Old Amount * (Rate[Old] / Rate[New])

        Args:
            money (Money): The money instance to convert.
            target_currency (Currency): The desired currency.

        Returns:
            Money: A new Money instance in the target currency.
        """
        if money.currency == target_currency:
            return money

        conversion_factor = self._rates[money.currency] / self._rates[target_currency]

        return replace(
            money, amount=money.amount * conversion_factor, currency=target_currency
        )

    @property
    def rates(self) -> dict[Currency, Decimal]:
        """
        Get a copy of the current exchange rates.

        Returns:
            dict[Currency, Decimal]: A copy of the rates dictionary.
        """
        return self._rates.copy()


class FinanceManager:
    """
    Manages the financial balance of an entity.

    Encapsulates a Money object and provides methods to deposit and withdraw funds safely.
    """

    def __init__(self, balance: Money = Money(0, Currency.USD)) -> None:
        """
        Initialize the Budget.

        Args:
            balance (Money): Initial funds. Defaults to 0 USD.
        """
        self._balance = balance
        self._transactions: list[Transaction] = []

    @property
    def currency(self) -> Currency:
        """Get the currency used by this budget."""
        return self._balance.currency

    @property
    def balance(self) -> Money:
        """Get the current balance."""
        return self._balance

    @property
    def history(self) -> list[Transaction]:
        return self._transactions[:]

    def _can_expense(self, money: Money) -> bool:
        """Check if there are sufficient funds for the expense."""
        return self._balance.amount >= money.amount

    def add_expense(self, money: Money, description: str = "") -> None:
        """
        Subtract funds from the budget.

        Args:
            money (Money): The amount to expense

        Raises:
            InsufficientBudgetError: If the balance is lower than the withdrawal amount.
            DifferentCurrenciesError: If the withdrawal currency doesn't match the budget.
        """
        self._balance.validate_currency(money)
        if not self._can_expense(money):
            raise InsufficientBudgetError(
                "There is not enough money in the budget to expense"
            )

        self._balance = self.balance - money

        t = Transaction(
            transaction_type=TransactionType.EXPENSE,
            amount=money,
            description=description,
        )
        self._transactions.append(t)

    def add_income(self, money: Money, description: str = "") -> None:
        """
        Add funds to the budget.

        Args:
            money (Money): The amount to deposit.

        Raises:
            DifferentCurrenciesError: If the deposit currency doesn't match the budget.
        """
        self._balance.validate_currency(money)
        self._balance = self.balance + money

        t = Transaction(
            transaction_type=TransactionType.INCOME,
            amount=money,
            description=description,
        )
        self._transactions.append(t)
