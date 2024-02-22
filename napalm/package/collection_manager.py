from importlib.metadata import entry_points

import loguru

from napalm.package.discovery import Collection
from napalm.plugins.installed import get_installed_tool_plugins

from napalm.package.detector_info import DetectorInfo
from typing import Dict, Optional
from toolz import memoize


class CollectionManager:
    """
    This class manages collections of plugins installed via pip.
    """

    @staticmethod
    def _pip_packages():
        """
        This method retrieves all installed pip packages that have a 'napalm.collection' entry point.
        It returns a dictionary where the keys are the package names and the values are the instantiated plugins.
        """
        plugins = {}

        # Iterate over all entry points in the 'napalm.collection' group
        for entry_point in entry_points(group="napalm.collection"):
            try:
                # Add the plugin configuration to the dictionary
                plugins[entry_point.name] = entry_point.load()()
            except Exception as e:
                loguru.logger.warning(
                    f"An error occurred while loading the plugin '{entry_point.name}'",
                    error=e,
                )
                loguru.logger.warning(e)

        return plugins

    def installed_collections(self):
        """
        This method yields the names of all collections from all installed pip packages that have a 'napalm.collection'
        entry point.
        """
        # Get all installed pip packages that have a 'napalm.collection' entry point
        packages = self._pip_packages()

        for plugin in get_installed_tool_plugins():
            if plugin.base_collection() is not None:
                yield plugin.base_collection().full_name

        # Iterate over all packages
        for package, collections in packages.items():
            # Iterate over all collections in the current package
            for collection in collections:
                # Yield the name of the current collection
                yield f"{package}/{collection.collection_name}"

    def get(self, collection_name: str) -> Collection:
        """
        This method returns the collection with the specified name from all installed pip packages that have a
        'napalm.collection' entry point.
        """
        try:
            package_name, collection_name = collection_name.split("/")
        except ValueError:
            package_name, collection_name = None, collection_name

        plugin_base = [
            plugin
            for plugin in get_installed_tool_plugins()
            if plugin.base_collection() is not None
            and plugin.base_collection().collection_name == collection_name
            and plugin.tool_name() == package_name
        ]

        if len(plugin_base) > 0:
            return plugin_base[0].base_collection()

        # Get all installed pip packages that have a 'napalm.collection' entry point
        packages = self._pip_packages()

        # Iterate over all packages
        for package, collections in packages.items():
            if package_name != package and package_name is not None:
                continue

            # Iterate over all collections in the current package
            for collection in collections:
                # Check if the current collection has the specified name
                if collection.collection_name == collection_name:
                    if collection.package_name is None:
                        collection.package_name = package
                    # Return the current collection
                    return collection

        # If no collection with the specified name was found, return None
        return None

    @memoize
    def detectors(self) -> Dict[str, DetectorInfo]:
        for collection in self.installed_collections():
            collection = self.get(collection)
            for detector in collection.detectors:
                yield detector.id, detector

    def get_detector(self, detector_rule_id: str) -> Optional[DetectorInfo]:
        return self.detectors().get(detector_rule_id, None)
