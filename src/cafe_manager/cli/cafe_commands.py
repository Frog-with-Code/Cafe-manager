import typer
from typing import Annotated

from .custom_types import Money, parse_money

app = typer.Typer()


@app.command()
def create(
    name: Annotated[
        str, typer.Option("--name", "-n", help="Name of the new cafe environment")
    ],
): ...


@app.command()
def remove(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the cafe",
        ),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            prompt="Warning! This operation is not reversible. Are you sure you want to delete this cafe?",
            confirmation_prompt=True,
        ),
    ] = False,
): ...


@app.command()
def activate(
    name: Annotated[
        str, typer.Option("--name", "-n", help="Name of the cafe environment")
    ],
): ...


@app.command()
def deactivate(): ...


@app.command()
def init(
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the cafe")],
    address: Annotated[
        str, typer.Option("--address", "-a", help="Address of the cafe")
    ],
    capital: Annotated[
        Money,
        typer.Option(
            "--capital", "-c", parser=parse_money, help="Starting capital of the cafe"
        ),
    ] = Money(),
): ...
