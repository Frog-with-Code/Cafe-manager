import typer
from typing import Annotated

from .validation import validate_item_format

app = typer.Typer()

@app.command()
def info(
    expanded: Annotated[
        bool, typer.Option("--expanded", "-e", help="Expand info table about menu")
    ] = False,
):
    """Show info about menu"""
    if expanded:
        print("HIIII")
    else:
        print("HUUUUUU")
        
@app.command("add-items")
def add_items(
    items: Annotated[
        list[str],
        typer.Argument(
            callback=lambda items: [validate_item_format(i) for i in items],
            help="Menu items in format name:amount",
        ),
    ],
):
    """Add new menu items to the menu"""
    print(items, sep="\n")


@app.command("remove-items")
def remove_items(
    items: Annotated[
        list[str],
        typer.Argument(
            callback=lambda items: [validate_item_format(i) for i in items],
            help="Menu items in format name:amount",
        ),
    ],
):
    """Remove menu items from the menu"""
    print(items, sep="\n")