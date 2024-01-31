from operator import add
from typing import List

import click
import rich
from toolz.curried import pipe, map, reduce, filter

from napalm.package.collection_manager import CollectionManager
from napalm.storage import StorageProvider
from napalm.storage.collection import CollectionStorage
from napalm.storage.workflow import WorkflowStorage

DEFAULT_COLLECTIONS = [
    "optimisations",  # inform
    "detectors",  # detect
    "indicators",  # direct
]
COLLECTION_TO_WORKFLOW = {
    "optimisations": "inform",
    "detectors": "detect",
    "indicators": "direct",
}


def auto_install_hook(storage_provider: StorageProvider):
    _new_collections(storage_provider)
    _removed_collections(storage_provider)


def _removed_collections(storage_provider: StorageProvider):
    removed_collections = list(_get_removed_collections(storage_provider))
    if not removed_collections:
        return

    console = rich.console.Console()

    console.print(
        "[bold]The following collections have been removed since you last ran napalm:[/bold]"
    )

    for collection in removed_collections:
        console.print(f" - [bold]{collection}[/bold]")

    if not click.confirm(
        "Would you like to automatically remove these collections from your workflows?",
        default=True,
    ):
        console.print("Skipping collection removal")
        return

    console.print("Removing collections...")
    _remove_collections(removed_collections, storage_provider)

    console.print("Successfully removed collections!")


def _new_collections(storage_provider: StorageProvider):
    installable_collections = list(_get_installable_collections(storage_provider))
    if not installable_collections:
        return

    console = rich.console.Console()

    console.print(
        "[bold]The following collections have been added since you last ran napalm:[/bold]"
    )

    can_auto_install = False
    has_non_default_collections = False
    for collection in installable_collections:
        collection_postfix = collection.split("/")[-1]
        workflow = COLLECTION_TO_WORKFLOW.get(collection_postfix, None)
        if workflow:
            can_auto_install = True
            console.print(
                f" - [bold]{collection}[/bold] (can be automatically added to [bold]{workflow}[/bold] workflow)"
            )
        else:
            has_non_default_collections = True
            console.print(f" - [bold]{collection}[/bold]")

    _mark_as_prompted(storage_provider, installable_collections)

    if not can_auto_install:
        console.print("No collections can be automatically added to your workflows")
        return

    if not click.confirm(
        "Would you like to automatically add these collections to your default workflows?",
        default=True,
    ):
        console.print("Skipping collection installation")
        return

    console.print("Installing collections...")
    _install_collections(installable_collections, storage_provider)
    console.print("Successfully installed collections!")

    if has_non_default_collections:
        console.print(
            "Note that some collections have been installed that are not part of the default workflows"
        )
        console.print(
            "You can add these to your workflows using the "
            "[bold]napalm workflow {name} add {collection name }[/bold] command"
        )


def _install_collections(collections: List[str], storage_provider: StorageProvider):
    workflow_storage = WorkflowStorage(storage_provider)

    for collection in collections:
        workflow_name = COLLECTION_TO_WORKFLOW.get(collection.split("/")[-1], None)
        if not workflow_name:
            continue
        workflow_storage.add_to_workflow(workflow_name, collection)


def _remove_collections(collections: List[str], storage_provider: StorageProvider):
    workflow_storage = WorkflowStorage(storage_provider)
    collection_storage = CollectionStorage(storage_provider)

    collection_storage.remove_prompted_installation(collections)

    for workflow in workflow_storage.list:
        remaining_collections = list(
            set(workflow_storage.get_workflow(workflow)) - set(collections)
        )
        workflow_storage.set_workflow(workflow, remaining_collections)


def _mark_as_prompted(storage_provider: StorageProvider, collections: List[str]):
    collection_storage = CollectionStorage(storage_provider)
    collection_storage.add_prompted_installation(collections)


def _get_installable_collections(storage_provider: StorageProvider):
    collection_storage = CollectionStorage(storage_provider)
    collection_manager = CollectionManager()

    installed_collections = collection_manager.installed_collections()
    prompted_installation = collection_storage.get_prompted_installation()
    new_collections = set(installed_collections) - set(prompted_installation)

    return new_collections


def _get_removed_collections(storage_provider: StorageProvider):
    collection_storage = CollectionStorage(storage_provider)
    workflow_storage = WorkflowStorage(storage_provider)
    collection_manager = CollectionManager()

    installed_collections = collection_manager.installed_collections()

    used_collections = pipe(
        workflow_storage.list,  # all workflow names
        map(
            lambda workflow: workflow_storage.get_workflow(workflow)
        ),  # all collections in each workflow
        filter(lambda x: x or x is []),  # remove None and False
        reduce(add),  # flatten
    )

    removed_collections = set(used_collections) - set(installed_collections)

    return removed_collections
