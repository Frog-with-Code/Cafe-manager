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
            "--price", "-p", help="Price of the chair", parser=parse_money
        ),
    ],
):
    pass


@app.command()
def discard(
    chair: Annotated[
        int,
        typer.Option("--chair", "-m", "--chair-id", help="Id of the chair", callback=validate_non_negative),
    ],
):
    pass