from typing import List

from loguru import logger

from .provider import StorageProvider


class WorkflowStorage:
    def __init__(self, storage: StorageProvider):
        self._storage = storage

        self._initialize_database()

    def _initialize_database(self):
        if self._storage.get("initialised/workflow-storage"):
            logger.debug("Collection storage already initialised")
            return
        logger.debug("Initialising meta collection storage")
        self._storage.set("workflows", ["detect", "direct", "inform"])

        self._storage.set("workflow/detect", [])
        self._storage.set("workflow/direct", [])
        self._storage.set("workflow/inform", [])

        self._storage.set("workflow/filters", {})

        self._storage.set("initialised/workflow-storage", True)
        logger.debug("Successfully initialised meta collection storage")

    @property
    def list(self):
        return self._storage.get("workflows")

    @property
    def filters(self):
        return self._storage.get("workflow/filters") or dict()

    def set_filter(self, workflow_name: str, filter_name: str, filter_value):
        filters = self.filters
        if workflow_name not in filters:
            filters[workflow_name] = dict()
        filters[workflow_name][filter_name] = filter_value
        self._storage.set("workflow/filters", filters)

    def get_filter(self, workflow_name: str, filter_name: str):
        filters = self.filters
        if workflow_name not in filters:
            return None
        return filters[workflow_name].get(filter_name, None)

    def create_workflow(self, name: str):
        if name in self.list:
            raise KeyError(f"Meta collection {name} already exists")
        self._storage.set("workflows", self.list + [name])
        self._storage.set(f"workflow/{name}", [])

    def remove_workflow(self, name: str):
        if name not in self.list:
            raise KeyError(f"Meta collection {name} does not exist")
        self._storage.set("workflows", self.list.remove(name))
        self._storage.delete(f"workflow/{name}")

    def get_workflow(self, name: str) -> List[str]:
        return self._storage.get(f"workflow/{name}")

    def set_workflow(self, name: str, collection: List[str]):
        if name not in self.list:
            raise KeyError(f"Meta collection {name} does not exist")
        self._storage.set(f"workflow/{name}", collection)

    def add_to_workflow(self, name: str, item: str):
        # Raise an error when the collection does not exist
        if name not in self.list:
            raise KeyError(f"Meta collection {name} does not exist")

        collection = self.get_workflow(name)

        if item in collection:
            return

        collection.append(item)
        self.set_workflow(name, collection)

    def remove_from_workflow(self, name: str, item: str):
        collection = self.get_workflow(name)
        collection.remove(item)
        self.set_workflow(name, collection)
