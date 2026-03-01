from enum import StrEnum
from uuid import UUID, uuid4

from .menu import MenuItem
from .finance import Money
from cafe_manager.common.exceptions import (
    OrderStateError,
    OrderModificationError,
    OrderPaymentError,
)


class OrderState(StrEnum):
    AWAITING_PAYMENT = "awaiting-payment"
    PAID = "paid"
    IN_PROGRESS = "in-progress"
    READY = "ready"
    CANCELLED = "cancelled"


class Order:
    def __init__(
        self,
        client_id: UUID,
        table_id: UUID | None = None,
        items: dict[MenuItem, int] | None = None,
    ) -> None:
        self.client_id = client_id
        self.table_id = table_id
        self.order_id = uuid4()
        self.employee_id = None
        self._items = items if items else {}

        self.total_price: Money = self._calculate_price(items)
        self._state = OrderState.AWAITING_PAYMENT

    def _calculate_price(self, items: dict[MenuItem, int] | None) -> Money:
        price = Money()
        if items:
            for item, amount in items.items():
                price += item.price * amount
        return price

    def add_item(self, item: MenuItem, amount: int) -> None:
        if self._state != OrderState.AWAITING_PAYMENT:
            raise OrderStateError("Order is already paid or cancelled")

        self._items[item] = self._items.get(item, 0) + amount
        self.total_price += item.price * amount

    def can_remove(self, item: MenuItem, amount: int) -> bool:
        if item not in self._items:
            return False
        if self._items[item] < amount:
            return False
        return True

    def remove_item(self, item: MenuItem, amount: int) -> None:
        if self._state != OrderState.AWAITING_PAYMENT:
            raise OrderStateError("Order is already paid or cancelled")

        if not self.can_remove(item, amount):
            raise OrderModificationError(f"There is not {amount} {item} in the order")
        self._items[item] -= amount
        self.total_price -= item.price * amount

    def can_be_paid(self) -> bool:
        if self._state != OrderState.AWAITING_PAYMENT:
            return False
        if len(self._items) <= 0:
            return False
        if self.total_price.amount == 0:
            return False
        return True

    def pay(self) -> None:
        if not self.can_be_paid():
            raise OrderPaymentError("Impossible to pay order due to inner properties")

        self._state = OrderState.PAID
        print("Order is paid")

    def start_cooking(self) -> None:
        match (self._state):
            case OrderState.AWAITING_PAYMENT:
                raise OrderStateError("Order is not paid")
            case OrderState.PAID:
                self._state = OrderState.IN_PROGRESS
                print("Order is cooking")
            case _:
                raise OrderStateError("Order is already cooked or cancelled")

    def end_cooking(self) -> None:
        if self._state != OrderState.IN_PROGRESS:
            raise OrderStateError("Order is not cooking")

        self._state = OrderState.READY
        print(f"Order {self.order_id} is ready")

    def cancel(self) -> None:
        match (self._state):
            case OrderState.AWAITING_PAYMENT:
                self._state = OrderState.CANCELLED
                print(f"Order {self.order_id} was cancelled")
            case OrderState.CANCELLED:
                print("Order is already cancelled")
            case _:
                raise OrderStateError("Impossible to cancel paid order")
