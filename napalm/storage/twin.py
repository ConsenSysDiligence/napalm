from typing import List, Set, Optional

from loguru import logger
from toolz import reduce, cons, filter

from .provider import StorageProvider


class TwinStorage:
    def __init__(self, storage: StorageProvider):
        self._storage = storage

        self._initialize_database()

    def _initialize_database(self):
        if self._storage.get("initialised/twin-storage"):
            logger.debug("Twin storage already initialised")
            return

        logger.debug("Initialising collection storage")
        self._storage.set("twin/twins", [])
        self._storage.set("initialised/twin-storage", True)

        logger.debug("Successfully initialised twin storage")

    @property
    def twins(self) -> List[Set[str]]:
        return list(map(set, self._storage.get("twin/twins")))

    def add_twin(self, twin: Set[str]):
        # OPTIMISE: if the amount of twins is high then this becomes an area where we can optimise
        all_registered_twins = reduce(lambda x, y: x + y, self.twins, set())

        if twin.intersection(all_registered_twins):
            raise ValueError("One of the elements in the twin is already registered")

        value = list(cons(list(twin), self.twins))
        self._storage.set("twin/twins", value)

    def remove_twin(self, twin: Set[str]):
        self._storage.set("twin/twins", list(filter(lambda x: x != twin, self.twins)))

    def replace_twin(self, twin: Set[str], new_twin: Set[str]):
        self.remove_twin(twin)
        self.add_twin(new_twin)

    def get_twin_for_member(self, member: str) -> Optional[Set[str]]:
        for twin in self.twins:
            if member in twin:
                return twin
        return None
