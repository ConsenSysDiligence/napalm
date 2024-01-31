import abc
from typing import Any


class StorageProvider:
    @abc.abstractmethod
    def get(self, key: str) -> Any:
        return

    @abc.abstractmethod
    def set(self, key: str, value: Any):
        return

    @abc.abstractmethod
    def delete(self, key: str):
        return
