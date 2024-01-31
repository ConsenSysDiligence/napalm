from napalm.storage.config import PersistentConfiguration
from napalm.storage.provider import StorageProvider
from napalm.storage.workflow import WorkflowStorage


def get_storage_provider(storage_type: str) -> StorageProvider:
    from napalm.storage.pickledb_provider import PickleProvider

    if storage_type == "pickle":
        return PickleProvider()
    else:
        raise Exception(f"Unknown storage type: {storage_type}")
