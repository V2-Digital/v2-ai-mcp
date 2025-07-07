"""V2.ai Insights Scraper MCP - A Model Context Protocol server for scraping and summarizing V2.ai blog posts."""

__version__ = "0.1.0"
__author__ = "Ashley Rodan"
__email__ = "ashley@example.com"

from .scraper import fetch_blog_post, fetch_blog_posts
from .summarizer import summarize

__all__ = ["fetch_blog_post", "fetch_blog_posts", "summarize"]
