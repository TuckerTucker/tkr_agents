# tools.py
from tkr_utils import logs_and_exceptions, setup_logging
from .tkr_simple_scrape_tool import simple_scrape, create_filename_from_url
from typing import Any, Dict
from abc import ABC, abstractmethod

# Set up the logger
logger = setup_logging(__file__)

class ToolInterface(ABC):
    @logs_and_exceptions(logger)
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass

class PageScrapeTool(ToolInterface):
    """
    A tool for scraping web pages, capable of exporting HTML content or converting it to Markdown.
    """
    @logs_and_exceptions(logger)
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Executes the web scraping tool.

        Args:
            params (Dict[str, Any]): Parameters for the web scraping, including:
                - url (str): The URL to scrape.
                - export_html (bool): Whether to export as HTML.
                - img_only (bool): Whether to extract images only.

        Returns:
            Dict[str, Any]: A dictionary containing the status and either the filename or an error message.
        """
        logger.info("Executing PageScrapeTool")
        url = params.get('url')
        export_html = params.get('export_html', False)
        img_only = params.get('img_only', False)

        if not url:
            logger.error("URL parameter is missing.")
            return {"status": "failure", "message": "URL parameter is missing"}

        result = simple_scrape(url, export_html, img_only)
        filename = create_filename_from_url(url, is_html=export_html, img_only=img_only)

        if result:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(result)
            logger.info(f"Content written to {filename}")
            return {"filename": filename, "status": "success"}
        else:
            logger.error("Failed to process the content properly.")
            return {"status": "failure", "message": "Failed to process the content properly"}

class GetWeatherTool(ToolInterface):
    @logs_and_exceptions(logger)
    def execute(self, params: Dict[str, Any]) -> Any:
        logger.info("Executing Mock GetWeatherTool")
        # Placeholder for getting weather logic
        return {"weather": "sunny"}
