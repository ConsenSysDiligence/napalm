import click
from rich.console import Console
from toolz.curried import pipe, map, reduce, filter

from napalm.package.collection import twins as twins_for_detectors
from napalm.package.collection_manager import CollectionManager
from napalm.storage.twin import TwinStorage


@click.group(help="View info on configured twins")
@click.pass_context
def twins(ctx):
    pass


@twins.command(help="List all twins")
@click.pass_context
def _list(ctx):
    ctx.ensure_object(dict)
    storage_provider = ctx.obj["storage"]
    twin_storage = TwinStorage(storage_provider)
    console = Console()

    if len(twin_storage.twins) == 0:
        console.print("No twins configured.")
        exit(0)

    console.print(f"[cyan]{len(twin_storage.twins)}[/cyan] twins configured:")
    for twin_set in twin_storage.twins:
        # twin set is a set of strings representing modules/ rules that detect the same issue
        console.print(f"  - {twin_set}")


@twins.command(help="List all builtin twins")
@click.pass_context
def builtin(ctx):
    collection_manager = CollectionManager()

    detectors = pipe(
        collection_manager.installed_collections(),
        map(collection_manager.get),
        filter(lambda m: m is not None),
        map(lambda m: m.detectors),
        reduce(lambda a, b: list(a) + list(b)),
    )
    collection_twins = twins_for_detectors(detectors)

    console = Console()

    console.print(f"[cyan]{len(collection_twins)}[/cyan] builtin twins:")
    for twin_set in collection_twins:
        # twin set is a set of strings representing modules/ rules that detect the same issue
        console.print(f"  - {twin_set}")


@twins.command(help="Add a twin")
@click.argument("base")
@click.argument("other")
@click.pass_context
def add(ctx, base: str, other: str):
    ctx.ensure_object(dict)
    storage_provider = ctx.obj["storage"]
    twin_storage = TwinStorage(storage_provider)

    console = Console()

    twin_1_twins = twin_storage.get_twin_for_member(base) or {}
    twin_2_twins = twin_storage.get_twin_for_member(other) or {}

    if twin_1_twins and twin_1_twins == twin_2_twins:
        console.print(f"Twin {base} and {other} already exist in {twin_1_twins}")
        exit(0)

    merge = False
    if twin_1_twins or twin_2_twins:
        if twin_1_twins:
            console.print(f"Twin {base} already exists in {twin_1_twins}")
        if twin_2_twins:
            console.print(f"Twin {other} already exists in {twin_2_twins}")

        merge = click.confirm("Do you want to merge these twins with your new one?")

        if not merge:
            console.print("Acknowledged! Exiting...")
            exit(0)

    if merge:
        if twin_1_twins:
            twin_storage.remove_twin(twin_1_twins)
        if twin_2_twins:
            twin_storage.remove_twin(twin_2_twins)
        new_set = twin_1_twins.union(twin_2_twins).union({base, other})

        twin_storage.add_twin(new_set)
        console.print(f"Merged twins {base} and {other} into {new_set}")
        exit(0)

    twin_storage.add_twin({base, other})
    console.print(f"Added twin {base} and {other}")


@twins.command(help="Remove a detector from twin pairs")
@click.argument("detector")
@click.pass_context
def remove(ctx, detector: str):
    ctx.ensure_object(dict)
    storage_provider = ctx.obj["storage"]
    twin_storage = TwinStorage(storage_provider)

    console = Console()

    twin_set = twin_storage.get_twin_for_member(detector)

    if twin_set is None:
        console.print(f"Detector {detector} is not part of a twin set")
        exit(0)

    twin_storage.remove_twin(twin_set)
    twin_storage.add_twin(twin_set.difference({detector}))
    console.print(f"Removed twin {detector} from {twin_set}")
