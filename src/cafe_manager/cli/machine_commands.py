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
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="Model of the coffee-machine"),
    ],
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help="Working cycles amount before maintenance",
            callback=validate_non_negative,
        ),
    ] = 1000,
):
    pass


@app.command()
def discard(
    machine: Annotated[
        int,
        typer.Option("--machine", "-m", "--machine-id", help="Id of the coffee-machine", callback=validate_non_negative),
    ],
):
    pass


@app.command()
def service(
    machine: Annotated[
        int,
        typer.Option("--machine", "-m", "--machine-id", help="Id of the coffee-machine", callback=validate_non_negative),
    ],
):
    pass
