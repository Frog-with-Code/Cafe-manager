import typer
from typing import Annotated

from .custom_types import Money, parse_money
from cafe_manager.infrastructure.sqlite.env_manager import EnvironmentManager
from cafe_manager.applications.use_cases.cafe_handlers import *
from cafe_manager.infrastructure.sqlite.repositories.cafe_repo import SQLiteCafeRepo


from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

app = typer.Typer()

env_manager = EnvironmentManager()


@app.command()
def create(
    name: Annotated[
        str, typer.Option("--name", "-n", help="Name of the new cafe environment")
    ],
):
    """Create new cafe environment"""
    try:
        handler = CafeCreateHandler(BASE_DIR, env_manager)
        handler.handle(name)
        print(f"New cafe environment with name {name} was created")
    except CafeEnvExistsError as e:
        typer.echo(f"{e}", err=True)
        typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error {e}", err=True)
        typer.Exit(code=1)


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
        ),
    ] = False,
):
    """Remove cafe environment"""
    try:
        if force:
            handler = CafeRemoveHandler(BASE_DIR, env_manager, BASE_DIR)
            handler.handle(name)
            print(f"Cafe environment with name {name} was deleted")
    except CafeEnvNotFoundError as e:
        typer.echo(f"{e}", err=True)
        typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error {e}", err=True)
        typer.Exit(code=1)


@app.command()
def activate(
    name: Annotated[
        str, typer.Option("--name", "-n", help="Name of the cafe environment")
    ],
):
    """Activate cafe environment"""
    try:
        handler = CafeActivateHandler(BASE_DIR, env_manager, BASE_DIR)
        handler.handle(name)
        print(f"Cafe environment with name {name} was activated")
    except CafeEnvNotFoundError as e:
        typer.echo(f"{e}", err=True)
        typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error {e}", err=True)
        typer.Exit(code=1)


@app.command()
def deactivate():
    """Deactivate cafe environment"""
    try:
        handler = CafeDeactivateHandler(BASE_DIR, env_manager, BASE_DIR)
        handler.handle()
        print(f"Cafe environment was deactivated")
    except CafeEnvNoActiveError as e:
        pass
    except Exception as e:
        typer.echo(f"Unexpected error {e}", err=True)
        typer.Exit(code=1)


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
