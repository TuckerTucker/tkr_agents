from toolbox.tools import PageScrapeTool, GetWeatherTool
from tkr_utils.llm import OpenAILLM
from agents.tkr_agent import Agent
from tkr_utils import setup_logging

logger = setup_logging(__file__)

# List tools available to the agent
tools = {
    "PageScrapeTool": (PageScrapeTool, "Scrapes web pages and can export HTML or Markdown."),
    "GetWeatherTool": (GetWeatherTool, "Provides weather information based on location.")
}

# Instantiate the LLM
llm_instance = OpenAILLM()

# Instantiate the Agent with the llm and tools
agent = Agent(llm=llm_instance, tools=tools)

# A query with params
query = "Scrape data from https://offhourscreative.com"

response = agent.process_query(query)
logger.info(response)