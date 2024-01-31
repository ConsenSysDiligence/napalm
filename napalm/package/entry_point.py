import os

from loguru import logger

from napalm.package.collection_manager import CollectionManager
from napalm.package.discovery import get_collections
from napalm.storage import WorkflowStorage, get_storage_provider


def entry_point(package):
    return get_collections(package)
