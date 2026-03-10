import typer
from typing import Annotated

app = typer.Typer()


@app.command()
def hire(
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the employee")],
):
    pass

@app.command()
def fire(
    id: Annotated[str, typer.Option(help="Id of the employee")],
):
    pass