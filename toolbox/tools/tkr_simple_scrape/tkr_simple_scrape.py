# tkr_simple_scrape.py
import logging
import requests
import html2text
from typing import Optional
from bs4 import BeautifulSoup
import re
import yaml
from tkr_utils import logs_and_exceptions, setup_logging

# Set up the logger
logger = setup_logging(__file__)

def load_config(config_file: str = "config.yaml") -> dict:
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

config = load_config('toolbox/tools/tkr_simple_scrape/config.yaml')

@logs_and_exceptions(logger)
def html_to_markdown(html: str) -> str:
    """
    Converts HTML content to Markdown format.
    """
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    markdown = converter.handle(html)
    return markdown

@logs_and_exceptions(logger)
def create_directory_from_url(url: str) -> str:
    """
    Creates a valid directory name from a URL by extracting the domain and modifying it.
    """
    domain = re.sub(r'^https?://(www\.)?', '', url)
    directory_name = re.sub(r'[^a-zA-Z0-9]', '_', domain).strip('_')
    return directory_name

@logs_and_exceptions(logger)
def create_filename_from_url(url: str, is_html: bool = False, img_only: bool = False) -> str:
    """
    Creates a valid filename from a URL by removing the protocol and other adjustments.
    """
    filename = re.sub(r'^https?://(www\.)?', '', url)
    filename = re.sub(r'[^a-zA-Z0-9]', '-', filename).strip('-')
    if img_only:
        filename += '.img-only'
    extension = '.html' if is_html else '.md'
    return filename + extension

@logs_and_exceptions(logger)
def simple_scrape(url: str, export_html: bool = False, img_only: bool = False) -> Optional[str]:
    """
    Extracts webpage data and converts it based on export format or needs.
    """
    logging.info(f"Fetching content from URL: {url}")
    headers = {'User-Agent': config["user_agent"]}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for tag in soup(config['tags_to_remove']):
            tag.decompose()

        if img_only:
            images = soup.find_all('img')
            list_html = "<ul>" + "".join(
                f"<li><img src='{img['src']}' alt='{img.get('alt', '')}'></li>"
                for img in images if img.has_attr('src')
            ) + "</ul>"
            return list_html

        if export_html:
            return str(soup)

        body_content = soup.find('body')
        if body_content is None:
            logging.warning("No <body> tag found in the HTML content.")
            return None

        html_content = str(body_content)
        markdown_content = html_to_markdown(html_content)
        if not markdown_content.strip():
            logging.warning("Empty content after Markdown conversion.")
            return None

        return markdown_content

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the website: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return None
