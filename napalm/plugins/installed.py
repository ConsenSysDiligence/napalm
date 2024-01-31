from importlib.metadata import entry_points

import loguru

from toolz import memoize


@memoize
def get_installed_tool_plugins():
    def plugins():
        points = entry_points(group="slither_analyzer.plugin")
        for entry_point in entry_points(group="napalm.tool_plugin"):
            try:
                yield entry_point.load()()
            except Exception as e:
                loguru.logger.warning(
                    f"An error occurred while loading the plugin '{entry_point.name}'",
                    error=e,
                )

    return list(plugins())
