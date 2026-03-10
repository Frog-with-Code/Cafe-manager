import typer
from typing import Annotated

from .validation import validate_non_negative
from .custom_types import Money, parse_money

app = typer.Typer()


@app.command()
def buy(
    price: Annotated[
        Money,
        typer.Option(
            "--price", "-p", help="Price of the coffee-machine", parser=parse_money
        ),
    ],
    seats: Annotated[
        int,
        typer.Option(
            "--seats",
            "-s",
            help="People capacity (max seats) of the table",
            callback=validate_non_negative,
        ),
    ] = 1000,
):
    pass


@app.command()
def discard(
    table: Annotated[
        int,
        typer.Option(
            "--table",
            "-t",
            "--table-id",
            help="Id of the table",
            callback=validate_non_negative,
        ),
    ],
):
    pass


@app.command()
def reserve(
    seats: Annotated[
        int,
        typer.Option(
            "--seats", "-s", help="Amount of people", callback=validate_non_negative
        ),
    ],
):
    """Reserve table"""
    pass


@app.command()
def free(
    table: Annotated[
        str, typer.Option("--table", "--table-id", "-t", help="Id of the table")
    ],
):
    pass
