from pathlib import Path
from typing import Callable, Any
from functools import wraps


def ensure_dir(path: str | Path):
    def decorator(func: Callable[[str], None]) -> Callable[[str], None]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            p = Path(path)
            if not p.exists() or not p.is_dir():
                p.mkdir(parents=True, exist_ok=True)
            wrapper.dir = str(p.resolve())
            func(*args, **kwargs)
        wrapper.dir = path
        return wrapper
    return decorator

def ensure_activated(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        active_file = Path(".active")
        if not active_file.exists():
            return FileExistsError("Cafe is not selected")
        return func(args, kwargs)
    return wrapper