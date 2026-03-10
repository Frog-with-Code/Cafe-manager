from cafe_manager.domain.entities.finance import Money

def parse_money(value: str):
    return Money.from_any(value)