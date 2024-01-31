from .provider import StorageProvider


class PersistentConfiguration:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    @property
    def default_meta_collection(self):
        return self.storage.get("configuration/default-meta-collection")
