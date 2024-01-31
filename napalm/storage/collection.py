from typing import List
from typing import Union

from loguru import logger

from .provider import StorageProvider


class CollectionStorage:
    def __init__(self, storage: StorageProvider):
        self._storage = storage

        self._initialize_database()

    def _initialize_database(self):
        if self._storage.get("initialised/collection-storage"):
            logger.debug("Collection storage already initialised")
            return

        logger.debug("Initialising collection storage")
        self._storage.set("collection/prompted-installation", [])
        self._storage.set("initialised/collection-storage", True)

        logger.debug("Successfully initialised collection storage")

    def get_prompted_installation(self) -> List[str]:
        return self._storage.get("collection/prompted-installation")

    def add_prompted_installation(self, collection: Union[str, List[str]]):
        if isinstance(collection, str):
            collection = [collection]

        collections = self.get_prompted_installation()

        collections.extend(collection)
        self._storage.set("collection/prompted-installation", collections)

    def remove_prompted_installation(self, collection: Union[str, List[str]]):
        if isinstance(collection, str):
            collection = [collection]

        collections = self.get_prompted_installation()

        for item in collection:
            collections.remove(item)

        self._storage.set("collection/prompted-installation", collections)
