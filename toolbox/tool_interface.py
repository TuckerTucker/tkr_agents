# tools.py
from tkr_utils import logs_and_exceptions, setup_logging
from abc import ABC, abstractmethod
from typing import Any, Dict

# Set up the logger
logger = setup_logging(__file__)

class ToolInterface(ABC):
    @logs_and_exceptions(logger)
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass
