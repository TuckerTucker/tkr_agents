from tkr_utils import logs_and_exceptions, setup_logging
from tkr_utils.extract_url import extract_url
from typing import Any, Dict, Type, Tuple, Optional
from tkr_utils.llm import LLMInterface
from toolbox.toolbox import ToolBox
from toolbox.tools import ToolInterface
from prompts.prompt import Prompt
from prompts.toolbox_prompts import toolbox_system_prompt, toolbox_agent_prompt, toolbox_task_prompt
import json

# Set up the logger
logger = setup_logging(__file__)

class Agent:
    """
    Manages interactions between the user, tools, and language models to process queries.
    """
    @logs_and_exceptions(logger)
    def __init__(self, llm: LLMInterface, tools: Dict[str, Tuple[Type[ToolInterface], str]]):
        self.llm = llm
        self.tools = ToolBox()
        for tool_name, (tool_class, description) in tools.items():
            self.tools.store(tool_name, tool_class(), description)
        self.prompt = Prompt()

    @logs_and_exceptions(logger)
    def process_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> str:
        logger.info("Processing query: %s", query)
        
        # Initialize params if not provided
        if params is None:
            params = {}

        # Extract URL from the query and update params if a URL is found
        extracted_url = extract_url(query)
        if extracted_url:
            params['url'] = extracted_url
            logger.info(f"Extracted URL from query: {extracted_url}")

        tool_descriptions = self.tools.get_tool_descriptions()
        system_prompt = toolbox_system_prompt.replace("{{available_tools_and_descriptions}}", tool_descriptions)
        
        self.prompt.add_system_prompt(system_prompt)
        self.prompt.add_agent_prompt(toolbox_agent_prompt)
        self.prompt.add_task_prompt(f"{toolbox_task_prompt} The user query is: {query}")
        
        full_prompt = self.prompt.get_full_prompt()
        
        llm_response = self.llm.query(full_prompt)
        logger.info("LLM response: %s", llm_response.choices[0].message.content)
        
        tool_needed, tool_params = self.choose_tool(llm_response.choices[0].message.content)
        if tool_needed:
            tool = self.tools.retrieve(tool_needed)
            if isinstance(tool_params, dict):
                # Merge the tool_params with the provided params
                tool_params.update(params)
                tool_response = tool.execute(params=tool_params)
                logger.info("Tool response: %s", tool_response)
                return str(tool_response)
            else:
                logger.error("Tool parameters are not in the expected dictionary format.")
                return "Tool parameters are not in the expected dictionary format."
        else:
            return "No appropriate tool found or tool not needed"

    @logs_and_exceptions(logger)
    def choose_tool(self, llm_response: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Parses the LLM response and determines the appropriate tool and its inputs based on the response.

        Args:
            llm_response (str): The JSON response from the language model.

        Returns:
            Tuple[Optional[str], Dict[str, Any]]: A tuple containing the name of the tool and a dictionary of parameters for the tool.
        """
        logger.info("Choosing tool based on LLM response")
        try:
            logger.debug(f"LLM response: {llm_response}")
            response_data = json.loads(llm_response)
            tool_name = response_data.get("tool")
            tool_inputs = response_data.get("tool_inputs")
            logger.debug(f"Parsed tool name: {tool_name}, tool inputs: {tool_inputs}")
            
            if tool_name in self.tools.tools:
                logger.info(f"Tool chosen: {tool_name} with inputs {tool_inputs}")
                # Ensure tool_inputs is a dictionary
                if isinstance(tool_inputs, str):
                    logger.warning("Tool inputs are in string format, converting to dictionary.")
                    tool_inputs = {"url": tool_inputs}  # Assuming 'url' is the key for the input
                return tool_name, tool_inputs
            else:
                logger.info("No specific tool identified or tool not available in ToolBox.")
                return None, {}

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding LLM response: {e}")
            return None, {}