import os
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    current_key = None
    current_value = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            if current_key is not None:
                os.environ.setdefault(current_key, current_value)
            key, value = line.split("=", 1)
            current_key = key.strip()
            current_value = value.strip()
            continue
        if current_key is not None:
            current_value += line
    if current_key is not None:
        os.environ.setdefault(current_key, current_value)
