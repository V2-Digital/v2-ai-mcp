import os
from typing import Any

from fastmcp import FastMCP

from .contentful_client import ContentfulClient, fetch_contentful_posts
from .summarizer import summarize

# Initialize FastMCP server
mcp = FastMCP("V2 Insights Scraper")


def _get_latest_posts(limit: int = 10):
    """Retrieves the latest blog posts with metadata from Contentful"""
    return _get_contentful_posts(limit)


def _summarize_post(post_id: str):
    """Returns a summary of the blog post with the specified ID"""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }

    try:
        client = ContentfulClient()
        post = client.fetch_single_post(
            post_id, content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost")
        )

        if "error" in post.get("content", ""):
            return post

        summary = summarize(post["content"])
        return {
            "title": post["title"],
            "date": post["date"],
            "author": post["author"],
            "url": post["url"],
            "summary": summary,
        }
    except Exception as e:
        return {"error": f"Error summarizing post: {str(e)}"}


def _get_post_content(post_id: str):
    """Returns the full content of the blog post with the specified ID"""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }

    try:
        client = ContentfulClient()
        return client.fetch_single_post(
            post_id, content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost")
        )
    except Exception as e:
        return {"error": f"Error fetching post: {str(e)}"}


def _get_contentful_posts(limit: int = 10):
    """Fetch posts directly from Contentful (if configured)"""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }

    try:
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
        client = ContentfulClient()
        return client.search_blog_posts(
            query=query,
            content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost"),
            limit=limit,
        )
    except Exception as e:
        return {"error": f"Error searching Contentful: {str(e)}"}


def _advanced_search_blogs(
    query: str,
    limit: int = 10,
    author_name: str | None = None,
    title_exact: str | None = None,
    published_after: str | None = None,
    published_before: str | None = None,
) -> list[dict[str, Any]]:
    """Advanced search with multiple filter options."""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return [
            {
                "title": "Configuration Error",
                "date": "",
                "author": "",
                "content": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables.",
                "url": "",
                "id": "",
            }
        ]

    try:
        client = ContentfulClient()
        return client.advanced_search_blog_posts(
            query=query,
            content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost"),
            limit=limit,
            author_name=author_name,
            title_exact=title_exact,
            published_after=published_after,
            published_before=published_before,
        )
    except Exception as e:
        return [
            {
                "title": "Search Error",
                "date": "",
                "author": "",
                "content": f"Error in advanced search: {str(e)}",
                "url": "",
                "id": "",
            }
        ]


def _search_by_author(author_name: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search blog posts by author name."""
    if not os.getenv("CONTENTFUL_SPACE_ID") or not os.getenv("CONTENTFUL_ACCESS_TOKEN"):
        return [
            {
                "title": "Configuration Error",
                "date": "",
                "author": "",
                "content": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables.",
                "url": "",
                "id": "",
            }
        ]

    try:
        client = ContentfulClient()
        return client.search_blog_posts(
            query="",  # Empty query to search all
            content_type=os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost"),
            limit=limit,
            author_filter=author_name,
        )
    except Exception as e:
        return [
            {
                "title": "Author Search Error",
                "date": "",
                "author": "",
                "content": f"Error searching by author: {str(e)}",
                "url": "",
                "id": "",
            }
        ]


# Register tools with FastMCP
@mcp.tool()
def get_latest_posts(limit: int = 10):
    """Retrieves the latest blog posts with metadata from Contentful"""
    return _get_latest_posts(limit)


@mcp.tool()
def summarize_post(post_id: str):
    """Returns a summary of the blog post with the specified Contentful entry ID"""
    return _summarize_post(post_id)


@mcp.tool()
def get_post_content(post_id: str):
    """Returns the full content of the blog post with the specified Contentful entry ID"""
    return _get_post_content(post_id)


@mcp.tool()
def get_contentful_posts(limit: int = 10):
    """Fetch posts directly from Contentful CMS (alias for get_latest_posts)"""
    return _get_contentful_posts(limit)


@mcp.tool()
def search_blogs(query: str, limit: int = 10):
    """Search blog posts across all content using text query. Searches titles, content, authors, and other fields."""
    return _search_blogs(query, limit)


@mcp.tool()
def advanced_search_blogs(
    query: str,
    limit: int = 10,
    author_name: str | None = None,
    title_exact: str | None = None,
    published_after: str | None = None,
    published_before: str | None = None,
):
    """Advanced search with multiple filter options.

    Args:
        query: Main search term to look for in blog titles
        limit: Maximum number of results (default: 10)
        author_name: Filter by author name (partial match)
        title_exact: Exact title match
        published_after: ISO date string (e.g., "2024-01-01") - posts published after this date
        published_before: ISO date string (e.g., "2024-12-31") - posts published before this date
    """
    return _advanced_search_blogs(
        query, limit, author_name, title_exact, published_after, published_before
    )


@mcp.tool()
def search_by_author(author_name: str, limit: int = 10):
    """Search blog posts by author name.

    Args:
        author_name: Author name to search for (partial match supported)
        limit: Maximum number of results (default: 10)
    """
    return _search_by_author(author_name, limit)


if __name__ == "__main__":
    mcp.run()
