from importlib import resources
from types import ModuleType
from typing import Generator

from napalm.plugins.installed import get_installed_tool_plugins
from napalm.package.collection import Collection


def _get_yaml_files(anchor):
    with resources.as_file(anchor) as collection_path:
        # it's not regex
        for yaml_file in collection_path.rglob("*.yml"):
            yield yaml_file
        for yaml_file in collection_path.rglob("*.yaml"):
            yield yaml_file


def _get_semgrep_configurations(anchor):
    # TODO: check if the yaml file is a semgrep configuration
    for yaml_file in _get_yaml_files(anchor):
        yield yaml_file


def get_collections(module: ModuleType) -> Generator[Collection, None, None]:
    module_traverser = resources.files(module)

    # top level directories are what distinguish collections
    for collection_dir in module_traverser.iterdir():
        if not collection_dir.is_dir():
            continue
        if collection_dir.name.startswith("_"):
            continue

        plugin_detectors = {
            plugin.tool_name(): list(plugin.discover_modules(collection_dir))
            for plugin in get_installed_tool_plugins()
        }

        yield Collection(
            collection_name=collection_dir.name,
            semgrep_configurations=list(_get_semgrep_configurations(collection_dir)),
            plugin_detectors=plugin_detectors,
        )
