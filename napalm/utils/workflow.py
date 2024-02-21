from napalm.storage.workflow import WorkflowStorage
from napalm.storage import StorageProvider
from napalm.package.collection_manager import CollectionManager
from typing import List


def get_collections_for_workflow(storage: StorageProvider, workflow: str) -> List[str]:
    if workflow == "all":
        collection_manager = CollectionManager()
        return collection_manager.installed_collections()

    workflow_storage = WorkflowStorage(storage)
    return workflow_storage.get_workflow(workflow)
