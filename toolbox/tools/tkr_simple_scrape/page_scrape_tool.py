# page_scrape_tool.py
from tkr_utils import logs_and_exceptions, setup_logging, AppPaths
from toolbox.tool_interface import ToolInterface
from typing import Any, Dict
from .tkr_simple_scrape import simple_scrape, create_filename_from_url, create_directory_from_url
import os

# Set up the logger
logger = setup_logging(__file__)

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

        directory_name = create_directory_from_url(url)
        AppPaths.add(directory_name)
        dir_path = os.path.join(AppPaths.LOCAL_DATA, directory_name)

        result = simple_scrape(url, export_html, img_only)
        if result:
            filename = create_filename_from_url(url, is_html=export_html, img_only=img_only)
            file_path = os.path.join(dir_path, filename)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(result)

            logger.info(f"Content written to {file_path}")
            return {"filename": file_path, "status": "success"}
        else:
            logger.error("Failed to process the content properly.")
            return {"status": "failure", "message": "Failed to process the content properly"}
