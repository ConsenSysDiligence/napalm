from pathlib import Path
from typing import Any

import pickledb

from .provider import StorageProvider


def _database_file():
    home = Path.home()
    napalm_home = home / ".napalm"
    napalm_home.mkdir(exist_ok=True)

    return napalm_home / "data.db"


class PickleProvider(StorageProvider):
    def __init__(self):
        """Initialise"""
        self.db = pickledb.load(_database_file().__str__(), False)

    def get(self, key: str) -> Any:
        return self.db.get(key)

    def set(self, key: str, value: Any):
        self.db.set(key, value)
        self.db.dump()

    def delete(self, key: str):
        self.db.rem(key)
        self.db.dump()
