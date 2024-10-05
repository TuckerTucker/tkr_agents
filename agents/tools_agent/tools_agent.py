import os
import json
import yaml
from typing import Any, Dict, Optional, Tuple
from toolbox.toolbox import ToolBox
from tkr_utils import logs_and_exceptions, setup_logging
from tkr_utils.extract_url import extract_url
from tkr_utils.helper_openai import OpenAIHelper
from prompt.prompt import Prompt

# Initialize logger
logger = setup_logging(__file__)

class ToolsAgent:
    """Manages interactions between the user, tools, and language models to process queries."""

    @logs_and_exceptions(logger)
    def __init__(self, config_path: str = 'agents/tools_agent/config.yaml'):
        """Initializes the ToolsAgent with the configuration and necessary components."""
        self.config = self.load_config(config_path)

        if self.config['llm_type'] == "OpenAI":
            self.llm = OpenAIHelper()
        else:
            raise ValueError("Unsupported LLM type. Only 'OpenAI' is currently supported.")

        self.toolbox = ToolBox()
        self.prompt = Prompt()

        self.load_prompts()

    @logs_and_exceptions(logger)
    def load_config(self, path: str) -> Dict[str, Any]:
        """Loads configuration from a specified YAML file."""
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info("Loaded configuration")
            return config

    @logs_and_exceptions(logger)
    def load_prompts(self) -> None:
        """Loads system, agent, and task prompts from the `prompts.yaml` file."""
        with open(os.path.join(os.path.dirname(__file__), 'prompts.yaml'), 'r') as file:
            prompts = yaml.safe_load(file)
            self.system_prompt = prompts['system_prompt']
            self.agent_prompt = prompts['agent_prompt']
            self.task_prompt = prompts['task_prompt']
            logger.info("Loaded prompts")

    @logs_and_exceptions(logger)
    def process_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Process a user query, interacting with specified tools and the language model."""
        logger.info("Processing query: %s", query)

        if params is None:
            params = {}

        extracted_url = extract_url(query)
        if extracted_url:
            params['url'] = extracted_url
            logger.info(f"URL extracted from query: {extracted_url}")

        tool_descriptions = self.toolbox.get_tool_descriptions()
        system_prompt = self.system_prompt.replace("{{available_tools_and_descriptions}}", tool_descriptions)

        self.prompt.add_system_prompt(system_prompt)
        self.prompt.add_agent_prompt(self.agent_prompt)
        self.prompt.add_task_prompt(f"{self.task_prompt} The user query is: {query}")

        full_prompt = self.prompt.get_full_prompt()
        llm_response = self.llm.send_message(full_prompt)

        choices = llm_response.choices  # Access the choices attribute directly
        if choices:
            response_content = choices[0].message.content  # Directly access 'content' from 'message'
            logger.info("LLM response content: %s", response_content)
        else:
            logger.error("No choices found in LLM response.")
            response_content = ""
        logger.info("LLM response content: %s", response_content)

        tool_needed, tool_params = self.choose_tool(response_content)
        if tool_needed:
            try:
                tool = self.toolbox.retrieve(tool_needed)
                if isinstance(tool_params, dict):
                    tool_params.update(params)
                    tool_response = tool.execute(tool_params)
                    logger.info("Tool response: %s", tool_response)
                    return str(tool_response)
                else:
                    logger.error("Tool parameters are not in the expected dictionary format.")
                    return "Tool parameters are not in the expected dictionary format."
            except ValueError as e:
                logger.error(f"Error retrieving tool: {e}")
                return str(e)
        else:
            return "No appropriate tool found or tool not needed"

    @logs_and_exceptions(logger)
    def choose_tool(self, llm_response: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Determines the appropriate tool and inputs from the LLM response."""
        logger.info("Choosing tool based on LLM response")
        try:
            response_data = json.loads(llm_response)
            tool_name = response_data.get("tool")
            tool_inputs = response_data.get("tool_inputs")
            logger.debug(f"Parsed tool name: {tool_name}, tool inputs: {tool_inputs}")

            if tool_name in self.toolbox.tools:
                if isinstance(tool_inputs, str):
                    logger.warning("Tool inputs are in string format, converting to dictionary.")
                    tool_inputs = {"url": tool_inputs}
                return tool_name, tool_inputs
            else:
                logger.info("No specific tool identified or tool not available in ToolBox.")
                return None, {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding LLM response: {e}")
            return None, {}
