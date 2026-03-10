import typer
from typing import Annotated

app = typer.Typer()


@app.command("add-ingredient")
def add_ingredient(
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the ingredient")],
    unit: Annotated[str, typer.Option("--unit", "-u", help="Unit of the ingredient")],
):
    pass


@app.command("remove-ingredient")
def remove_ingredient(
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the ingredient")],
):
    pass


@app.command()
def supply(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Name of the ingredient"),
    ],
    amount: Annotated[
        float, typer.Option("--amount", "-a", help="Amount of ingredients")
    ],
    price: Annotated[
        float, typer.Option("--price", "-p", help="Total price of the operation")
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", prompt=f"Are you sure you want to buy ingredient?"
        ),
    ] = False,
):
    if force:
        print(name, amount, price)
