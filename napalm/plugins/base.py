from napalm.tool.tool_runner import ToolRunner
from typing import Optional, Callable

from abc import ABC, abstractmethod
from pathlib import Path
from napalm.package.collection import DetectorInfo, Collection


class ToolPlugin(ABC):
    @abstractmethod
    def tool_name(self) -> str:
        pass

    @abstractmethod
    def tool_runner(self) -> Optional[ToolRunner]:
        pass

    @abstractmethod
    def base_collection(self) -> Optional[Collection]:
        pass

    @abstractmethod
    def discover_modules(self, anchor):
        pass

    def detector_info(self, module) -> DetectorInfo:
        pass

    @abstractmethod
    def initialize_default_files(self, path: Path):
        pass

    @abstractmethod
    def instrument_command(self, command: Callable):
        pass
