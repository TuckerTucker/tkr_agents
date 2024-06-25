# toolbox/toolbox.py
from typing import Callable, Dict, Any
from tkr_utils import logs_and_exceptions, setup_logging

# Set up the logger
logger = setup_logging(__file__)

class ToolBox:
    """
    Manages a collection of tools, providing functionalities to store and retrieve tool descriptions and functionalities.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}
        logger.info("ToolBox initialized.")

    @logs_and_exceptions(logger)
    def store(self, tool_name: str, tool_func: Callable, description: str) -> None:
        """
        Stores a tool along with its function and description in the toolbox.

        Args:
            tool_name (str): The name of the tool.
            tool_func (Callable): The function associated with the tool.
            description (str): The description of the tool.
        """
        self.tools[tool_name] = tool_func
        self.descriptions[tool_name] = description
        logger.info(f"Tool {tool_name} stored in ToolBox with description.")

    @logs_and_exceptions(logger)
    def retrieve(self, tool_name: str) -> Callable:
        """
        Retrieves a tool's function by its name.

        Args:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Callable: The function associated with the tool.
        """
        tool_func = self.tools.get(tool_name)
        if tool_func:
            logger.info(f"Tool {tool_name} retrieved from ToolBox.")
            return tool_func
        else:
            logger.error(f"Tool {tool_name} not found in ToolBox.")
            raise ValueError(f"Tool {tool_name} not found in ToolBox.")

    @logs_and_exceptions(logger)
    def get_tool_descriptions(self) -> str:
        """
        Retrieves descriptions of all tools in the toolbox.

        Returns:
            str: A formatted string of tool descriptions.
        """
        descriptions = [f"{name}: {desc}" for name, desc in self.descriptions.items()]
        return "\n".join(descriptions)