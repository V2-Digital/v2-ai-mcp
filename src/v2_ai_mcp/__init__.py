"""V2.ai Insights MCP - A Model Context Protocol server for accessing and summarizing V2.ai blog posts from Contentful CMS."""

__version__ = "0.1.0"
__author__ = "Ashley Rodan"
__email__ = "ashley@example.com"

from .contentful_client import ContentfulClient, fetch_contentful_posts
from .summarizer import summarize

__all__ = ["ContentfulClient", "fetch_contentful_posts", "summarize"]
