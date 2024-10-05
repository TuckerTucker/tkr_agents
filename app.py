# app.py

from tkr_agents.agents.tools_agent.tools_agent import ToolsAgent
from tkr_utils import setup_logging

# Initialize logger
logger = setup_logging(__file__)

# Instantiate the ToolsAgent using the default config path
tools_agent = ToolsAgent()

# A query with params
query = "Scrape data from https://offhourscreative.com"

# Processing the query
response = tools_agent.process_query(query)

# Log the response
logger.info(response)
