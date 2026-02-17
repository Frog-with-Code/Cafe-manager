from ..common.utils import ensure_dir
from pathlib import Path

STORAGE_DIR = "cafes"

@ensure_dir(STORAGE_DIR)
def activate_cafe(cafe_name: str) -> None:
    cafe_file = Path(activate_cafe.dir) / f"{cafe_name}.json"
    if not cafe_file.exists() or not cafe_file.is_file():
        raise FileExistsError(f"Cafe {cafe_name} not exists")
    else:
        Path(".active").write_text(cafe_file.as_posix(), encoding="utf-8")
        print(f"Cafe {cafe_name} was activated")

@ensure_dir(STORAGE_DIR)
def create_cafe(cafe_name: str) -> None:
    cafe_file = Path(create_cafe.dir) / f"{cafe_name}.json"
    if cafe_file.exists():
        raise FileExistsError(f"Cafe {cafe_name} already exists")
    cafe_file.touch()
    print("New cafe was created")
    activate_cafe(cafe_name)
    
@ensure_dir(STORAGE_DIR)
def deactivate_cafe() -> None:
    Path(".active").unlink(missing_ok=True)
    print("Cafe was deactivated")
    
def get_active():
    return False
            
@ensure_dir(STORAGE_DIR)
def delete_cafe(cafe_name: str) -> None:
    cafe_file = Path(delete_cafe.dir) / f"{cafe_name}.json"
    if not cafe_file.exists() or not cafe_file.is_file():
        raise FileExistsError(f"Cafe {cafe_name} not exists")
    
    while True:
        choice = input(f"If you want to delete the cafe {cafe_name} print 'y'. Else print 'n': ")
        if choice in ('y', 'Y'):
            if get_active() == cafe_file:
                deactivate_cafe()
            Path(cafe_file).unlink()
            break
        elif choice in ('n', 'N'):
            break
        else:
            print("Unknown choice")
        