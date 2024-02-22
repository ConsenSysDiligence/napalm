from napalm.storage.workflow import WorkflowStorage
from napalm.storage import StorageProvider
from napalm.package.collection_manager import CollectionManager
from typing import List
import re


def get_collections_for_workflow(storage: StorageProvider, workflow: str) -> List[str]:
    workflow_storage = WorkflowStorage(storage)
    collection_manager = CollectionManager()

    if workflow == "all":
        return list(collection_manager.installed_collections())

    if re.match(r"(\S+)/\*", workflow):

        package = re.match(r"(\S+)/\*", workflow).group(1)
        collections = []
        for collection in collection_manager.installed_collections():
            collection = collection_manager.get(collection)
            if collection.package_name == package:
                collections.append(collection.full_name)
        return collections

    return workflow_storage.get_workflow(workflow)
