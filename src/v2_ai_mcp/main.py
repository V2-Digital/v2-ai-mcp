import os

from fastmcp import FastMCP

from .scraper import fetch_blog_posts
from .summarizer import summarize

# Initialize FastMCP server
mcp = FastMCP("V2 Insights Scraper")


def _get_latest_posts():
    """Retrieves the latest blog posts with metadata"""
    return fetch_blog_posts()


def _summarize_post(index: int):
    """Returns a summary of the blog post at the specified index"""
    posts = fetch_blog_posts()
    if 0 <= index < len(posts):
        post = posts[index]
        summary = summarize(post["content"])
        return {
            "title": post["title"],
            "date": post["date"],
            "author": post["author"],
            "url": post["url"],
            "summary": summary,
        }
    else:
        return {"error": f"Invalid index. Available posts: 0 to {len(posts) - 1}"}


def _get_post_content(index: int):
    """Returns the full content of the blog post at the specified index"""
    posts = fetch_blog_posts()
    if 0 <= index < len(posts):
        return posts[index]
    else:
        return {"error": f"Invalid index. Available posts: 0 to {len(posts) - 1}"}


def _get_contentful_posts(limit: int = 10):
    """Fetch posts directly from Contentful (if configured)"""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }

    try:
        from .contentful_client import fetch_contentful_posts

        return fetch_contentful_posts(
            content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost"), limit=limit
        )
    except Exception as e:
        return {"error": f"Error fetching from Contentful: {str(e)}"}


def _search_blogs(query: str, limit: int = 10):
    """Search blog posts across all content using Contentful's search API"""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }

    try:
        from .contentful_client import ContentfulClient

        client = ContentfulClient()
        return client.search_blog_posts(
            query=query,
            content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost"),
            limit=limit,
        )
    except Exception as e:
        return {"error": f"Error searching Contentful: {str(e)}"}


# Register tools with FastMCP
@mcp.tool()
def get_latest_posts():
    """Retrieves the latest blog posts with metadata"""
    return _get_latest_posts()


@mcp.tool()
def summarize_post(index: int):
    """Returns a summary of the blog post at the specified index"""
    return _summarize_post(index)


@mcp.tool()
def get_post_content(index: int):
    """Returns the full content of the blog post at the specified index"""
    return _get_post_content(index)


@mcp.tool()
def get_contentful_posts(limit: int = 10):
    """Fetch posts directly from Contentful CMS (if configured)"""
    return _get_contentful_posts(limit)


@mcp.tool()
def search_blogs(query: str, limit: int = 10):
    """Search blog posts across all content using text query. Searches titles, content, authors, and other fields."""
    return _search_blogs(query, limit)


if __name__ == "__main__":
    mcp.run()
