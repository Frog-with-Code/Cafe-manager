from pathlib import Path

from cafe_manager.domain.entities.cafe import Cafe
from cafe_manager.infrastructure.sqlite.env_manager import EnvironmentManager
from cafe_manager.common.exceptions import (
    CafeEnvExistsError,
    CafeEnvNoActiveError,
    CafeEnvNotFoundError,
    CafeInitError,
)
from cafe_manager.domain.entities.finance import Money, Account
from cafe_manager.infrastructure.interfaces import FinanceRepo, CafeRepo


class CafeCreateHandler:
    def __init__(self, env_folder_path: Path, env_manager: EnvironmentManager) -> None:
        self.base_path = env_folder_path
        self._env_manager = env_manager

    def handle(self, name: str) -> None:
        db_path = self.base_path / f"{name}.db"

        print(db_path)
        if db_path.exists():
            raise CafeEnvExistsError(
                f"Impossible to create cafe '{name}'. Such cafe already exists"
            )

        self._env_manager.create_env(db_path)


class CafeRemoveHandler:
    def __init__(
        self, env_folder_path: Path, env_manager: EnvironmentManager, data_folder: Path
    ) -> None:
        self.base_path = env_folder_path
        self._env_manager = env_manager
        self.data_folder = data_folder

    def handle(self, name: str) -> None:
        db_path = self.base_path / f"{name}.db"

        try:
            self._env_manager.remove_env(db_path)
            active_env = self._env_manager.get_active_env_path(self.data_folder)
            if active_env == db_path:
                self._env_manager.deactivate_env(self.data_folder)
        except FileNotFoundError as e:
            raise CafeEnvNotFoundError(f"Impossible to remove cafe '{name}'. Such cafe not exists") from e


class CafeActivateHandler:
    def __init__(
        self, env_folder_path: Path, env_manager: EnvironmentManager, data_folder: Path
    ) -> None:
        self.base_path = env_folder_path
        self.data_folder = data_folder
        self._env_manager = env_manager

    def handle(self, name: str) -> None:
        db_path = self.base_path / f"{name}.db"

        try:
            self._env_manager.activate_env(db_path, self.data_folder)
        except FileNotFoundError as e:
            raise CafeEnvNotFoundError(f"Impossible to activate cafe '{name}'. Such cafe not exists") from e


class CafeDeactivateHandler:
    def __init__(
        self, env_folder_path: Path, env_manager: EnvironmentManager, data_folder: Path
    ) -> None:
        self.base_path = env_folder_path
        self.data_folder = data_folder
        self._env_manager = env_manager

    def handle(self) -> None:
        try:
            self._env_manager.deactivate_env(self.data_folder)
        except FileNotFoundError as e:
            raise CafeEnvNoActiveError(
                "Impossible to deactivate. No active environments"
            )


class CafeInitHandler:
    def __init__(
        self, db_path: Path, cafe_repo: CafeRepo, account: FinanceRepo
    ) -> None:
        self.db_path = db_path
        self._cafe_repo = cafe_repo
        self._account = account

    def handle(self, name: str, address: str, startup_capital: Money) -> None:
        existing_cafe = self._cafe_repo.get()
        if not existing_cafe is None:
            raise CafeInitError("Cafe is already initialized")

        cafe = Cafe(name, address)
        account = Account(balance=startup_capital)

        self._cafe_repo.save(cafe)
        self._account.save(account)
