class Cafe:
    def __init__(
        self,
        name: str,
        menu: Menu = None,
        employees: set[Barista] = None,
        tables: list[Table] = None,
    ) -> None:
        self.name = name
        self.menu = menu
        self._employees = employees if employees else set()
        self._tables = tables if tables else list()
