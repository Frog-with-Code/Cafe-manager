import typer
from typing import Annotated

app = typer.Typer()


@app.command("list-pending")
def show_list_pending():
    """Shows query of paid orders"""
    pass


@app.command()
def start(
    employee: Annotated[
        str,
        typer.Option(
            "--employee", "--employee-id", "-e", help="Id of the order to start cooking"
        ),
    ],
):
    """Start cooking paid order"""
    print(employee)


@app.command()
def complete(
    order: Annotated[
        str,
        typer.Option("--order", "--order-id", "-o", help="Id of the order to complete"),
    ],
):
    """Complete order in progress"""
    print(order)
