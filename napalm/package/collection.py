from dataclasses import dataclass
from operator import add
from pathlib import Path
from typing import List, Type, Union, Dict, Set, Optional

from toolz import concat, map, reduce

from napalm.tool.semgrep_info import SemgrepConfiguration, SemgrepRule
from napalm.plugins.installed import get_installed_tool_plugins
from napalm.package.detector_info import DetectorInfo, CompetitionInfo


class Collection:
    def __init__(
        self,
        collection_name,
        semgrep_configurations: List[Path] = (),
        package_name: Optional[str] = None,
        plugin_detectors: Optional[Dict] = None,
    ):
        self.collection_name = collection_name
        self.package_name = package_name

        self.semgrep_configurations = semgrep_configurations

        self.plugin_detectors = plugin_detectors or dict()

    @property
    def full_name(self):
        return f"{self.package_name}/{self.collection_name}"

    @property
    def detectors(self) -> List[DetectorInfo]:
        plugin_detectors = list(
            concat(
                map(
                    lambda plugin: map(
                        plugin.detector_info,
                        self.plugin_detectors.get(plugin.tool_name(), []),
                    ),
                    get_installed_tool_plugins(),
                )
            )
        )
        return list(
            concat(
                [
                    map(
                        DetectorInfo.from_semgrep,
                        reduce(
                            add,
                            map(
                                lambda c: SemgrepConfiguration.from_yaml(c).rules,
                                self.semgrep_configurations,
                            ),
                            [],
                        ),
                    ),
                    plugin_detectors,
                ]
            )
        )


def twins(detectors: List[DetectorInfo]) -> List[Set[str]]:
    twin_map: Dict[str, Set[str]] = dict()
    result = []

    for detector in detectors:
        for twin in detector.twins:
            base = twin_map.get(detector.id, None)
            other = twin_map.get(twin, None)

            if base == other and base:
                continue

            if base and other:
                result.remove(other)
                twin_map[twin] = base
                base.update(other)

            if base:
                base.add(twin)
            elif other:
                other.add(detector.id)
            else:
                twin_set = {detector.id, twin}
                result.append(twin_set)
                twin_map[detector.id] = twin_set
                twin_map[twin] = twin_set

    return result
