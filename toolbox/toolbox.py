from typing import Callable, Dict, Any
import yaml
from pathlib import Path
from tkr_utils import logs_and_exceptions, setup_logging

# Set up the logger
logger = setup_logging(__file__)

class ToolBox:
    """
    Manages a collection of tools, providing functionalities to store and retrieve.
    """
    def __init__(self, config_file: str = 'toolbox/tools_config.yaml'):
        self.tools: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}
        logger.info("ToolBox initialized.")
        self.load_tools_from_config(config_file)

    @logs_and_exceptions(logger)
    def load_tools_from_config(self, config_file: str) -> None:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        for tool_config in config.get('tools', []):
            if tool_config['enabled']:
                tool_name = tool_config['name']
                description = tool_config['description']
                module = tool_config['module']
                class_name = tool_config['function']  # Assuming this is the class name
                logger.info(f"Loading Tool: {tool_name} | {description} | {module}")

                # Import the module and instantiate the tool
                tool_module = __import__(module, fromlist=[class_name])
                tool_class = getattr(tool_module, class_name)
                tool_instance = tool_class()  # Instantiate the tool class

                self.store(tool_name, tool_instance, description)  # Store the instance

    @logs_and_exceptions(logger)
    def store(self, tool_name: str, tool_func: Callable, description: str) -> None:
        """
        Stores a tool's function and description in the toolbox.
        """
        self.tools[tool_name] = tool_func
        self.descriptions[tool_name] = description
        logger.info(f"Tool {tool_name} stored with description.")

    @logs_and_exceptions(logger)
    def retrieve(self, tool_name: str) -> Callable:
        """
        Retrieves a tool's function by its name.
        """
        tool_func = self.tools.get(tool_name)
        if tool_func:
            logger.info(f"Tool {tool_name} retrieved from ToolBox.")
            return tool_func
        else:
            logger.error(f"Tool {tool_name} not found.")
            raise ValueError(f"Tool {tool_name} not found.")

    @logs_and_exceptions(logger)
    def get_tool_descriptions(self) -> str:
        """
        Retrieves descriptions of all tools in the toolbox.
        """
        descriptions = [f"{name}: {desc}" for name, desc in self.descriptions.items()]
        return "\n".join(descriptions)
