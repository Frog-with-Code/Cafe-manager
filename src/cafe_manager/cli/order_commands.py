import typer
from typing import Annotated

from .validation import validate_item_format, validate_non_negative
from .custom_types import Money, parse_money

app = typer.Typer(help="Commands for order management")


@app.command()
def create(
    items: Annotated[
        list[str],
        typer.Argument(
            callback=lambda items: [validate_item_format(i) for i in items],
            help="Menu items in format name:amount",
        ),
    ],
    table: Annotated[
        str | None,
        typer.Option(
            "--table",
            "--table-id" "-t",
            help="Id of the reserved table",
        ),
    ] = None,
):
    """Creates new order"""
    print(items, table, sep="\n")


@app.command()
def pay(
    order: Annotated[
        str,
        typer.Option("--order", "--order-id", "-o", help="Id of the order to pay for"),
    ],
    price: Annotated[
        Money,
        typer.Option(
            "--price", "-p", help="Money to pay for the order", parser=parse_money
        ),
    ],
    client: Annotated[
        str | None,
        typer.Option("--client", "--client-id", "-c", help="Id of the client"),
    ] = None,
):
    """Pay for the created order"""
    print(order, price, client, sep="\n")


@app.command("add-items")
def add_items(
    items: Annotated[
        list[str],
        typer.Argument(
            callback=lambda items: [validate_item_format(i) for i in items],
            help="Menu items in format name:amount",
        ),
    ],
    order: Annotated[
        str,
        typer.Option(
            "--order", "--order-id", "-o", help="Id of the order to add items into"
        ),
    ],
):
    """Add new menu items to the created order"""
    print(order, items, sep="\n")


@app.command("remove-items")
def remove_items(
    items: Annotated[
        list[str],
        typer.Argument(
            callback=lambda items: [validate_item_format(i) for i in items],
            help="Menu items in format name:amount",
        ),
    ],
    order: Annotated[
        str,
        typer.Option(
            "--order", "--order-id", "-o", help="Id of the order to remove items from"
        ),
    ],
):
    """Remove menu items from the created order"""
    print(order, items, sep="\n")


@app.command()
def info(
    expanded: Annotated[
        bool, typer.Option("--expanded", "-e", help="Expand info table about orders")
    ] = False,
):
    """Show info about orders"""
    if expanded:
        print("HIIII")
    else:
        print("HUUUUUU")


@app.command()
def cancel(
    order: Annotated[
        str, typer.Option("--order", "-o", "--order-id", help="Id of the order")
    ],
): 
    pass
