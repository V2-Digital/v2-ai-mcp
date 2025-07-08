"""Contentful CMS integration for fetching blog posts via GraphQL."""

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


class ContentfulClient:
    """Client for fetching content from Contentful CMS."""

    def __init__(
        self,
        space_id: str | None = None,
        access_token: str | None = None,
        environment: str = "master",
    ):
        """Initialize Contentful GraphQL client.

        Args:
            space_id: Contentful space ID (or from CONTENTFUL_SPACE_ID env var)
            access_token: Contentful access token (or from CONTENTFUL_ACCESS_TOKEN env var) - required for GraphQL API
            environment: Contentful environment (default: master)
        """
        self.space_id = space_id or os.getenv("CONTENTFUL_SPACE_ID")
        self.access_token = access_token or os.getenv("CONTENTFUL_ACCESS_TOKEN")
        self.environment = environment

        if not self.space_id:
            raise ValueError(
                "Contentful space_id is required. "
                "Set CONTENTFUL_SPACE_ID environment variable."
            )

        if not self.access_token:
            raise ValueError(
                "Contentful access_token is required for GraphQL API. "
                "Set CONTENTFUL_ACCESS_TOKEN environment variable."
            )

        self.graphql_url = f"https://graphql.contentful.com/content/v1/spaces/{self.space_id}/environments/{self.environment}"
        self.headers = {"Content-Type": "application/json"}

        # Add authorization header (required for GraphQL API)
        self.headers["Authorization"] = f"Bearer {self.access_token}"

    def fetch_blog_posts(
        self,
        content_type: str = "pageBlogPost",
        limit: int = 10,
        order: str = "sys_publishedAt_DESC",
    ) -> list[dict[str, Any]]:
        """Fetch blog posts from Contentful via GraphQL.

        Args:
            content_type: Content type ID for blog posts
            limit: Maximum number of posts to fetch
            order: Sort order (default: newest first)

        Returns:
            List of blog post dictionaries
        """
        query = f"""
        query {{
            {content_type}Collection(limit: {limit}, order: {order}) {{
                items {{
                    sys {{
                        id
                        publishedAt
                    }}
                    title
                    slug
                    content {{
                        json
                    }}
                    author {{
                        name
                    }}
                    publishedDate
                }}
            }}
        }}
        """

        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json={"query": query},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return self._error_response(f"GraphQL errors: {data['errors']}")

            items = (
                data.get("data", {})
                .get(f"{content_type}Collection", {})
                .get("items", [])
            )

            posts = []
            for item in items:
                post_data = self._extract_graphql_post_data(item)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
            logger.error(f"Error fetching from Contentful GraphQL: {e}")
            return self._error_response(f"Error: {str(e)}")

    def _error_response(self, error_message: str) -> list[dict[str, Any]]:
        """Create a standardized error response."""
        return [
            {
                "title": "Error fetching from Contentful",
                "date": "",
                "author": "",
                "content": error_message,
                "url": "",
                "id": "",
            }
        ]

    def _extract_graphql_post_data(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Extract blog post data from GraphQL response item."""
        try:
            # Extract basic fields
            title = item.get("title", "No title")
            slug = item.get("slug", "")

            # Extract content from rich text JSON
            content_json = item.get("content", {}).get("json", {})
            content = (
                self._extract_content_from_json(content_json)
                if content_json
                else "No content available"
            )

            # Extract author
            author_data = item.get("author", {})
            author = (
                author_data.get("name", "Unknown Author")
                if author_data
                else "Unknown Author"
            )

            # Extract date
            publish_date = item.get("publishedDate") or item.get("sys", {}).get(
                "publishedAt", ""
            )

            # Build URL
            url = f"https://v2.ai/insights/{slug}" if slug else ""

            # Get ID
            entry_id = item.get("sys", {}).get("id", "")

            return {
                "title": str(title),
                "date": str(publish_date),
                "author": str(author),
                "content": content,
                "url": url,
                "id": entry_id,
            }

        except Exception as e:
            logger.error(f"Error extracting GraphQL post data: {e}")
            return None

    def _extract_content_from_json(self, content_json: dict[str, Any]) -> str:
        """Extract plain text content from Contentful rich text JSON."""
        try:

            def extract_text_from_node(node):
                if isinstance(node, dict):
                    if node.get("nodeType") == "text":
                        return node.get("value", "")
                    elif "content" in node:
                        return " ".join(
                            extract_text_from_node(child) for child in node["content"]
                        )
                elif isinstance(node, list):
                    return " ".join(extract_text_from_node(child) for child in node)
                return ""

            if content_json and "content" in content_json:
                result = extract_text_from_node(content_json["content"])
                return str(result) if result else ""
            return ""

        except Exception as e:
            logger.error(f"Error extracting content from JSON: {e}")
            return ""

    def fetch_single_post(
        self, entry_id: str, content_type: str = "pageBlogPost"
    ) -> dict[str, Any]:
        """Fetch a single blog post by entry ID via GraphQL.

        Args:
            entry_id: Contentful entry ID
            content_type: Content type ID for blog posts

        Returns:
            Blog post dictionary
        """
        query = f"""
        query {{
            {content_type}(id: "{entry_id}") {{
                sys {{
                    id
                    publishedAt
                }}
                title
                slug
                content {{
                    json
                }}
                author {{
                    name
                }}
                publishedDate
            }}
        }}
        """

        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json={"query": query},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return {
                    "title": "Error fetching post",
                    "date": "",
                    "author": "",
                    "content": f"GraphQL errors: {data['errors']}",
                    "url": "",
                    "id": entry_id,
                }

            item = data.get("data", {}).get(content_type)
            if item:
                return self._extract_graphql_post_data(item) or {
                    "title": "Post not found",
                    "date": "",
                    "author": "",
                    "content": "Post data could not be extracted",
                    "url": "",
                    "id": entry_id,
                }
            else:
                return {
                    "title": "Post not found",
                    "date": "",
                    "author": "",
                    "content": "Post not found in Contentful",
                    "url": "",
                    "id": entry_id,
                }

        except Exception as e:
            logger.error(f"Error fetching single post: {e}")
            return {
                "title": "Error fetching post",
                "date": "",
                "author": "",
                "content": f"Error: {str(e)}",
                "url": "",
                "id": entry_id,
            }

    def search_blog_posts(
        self,
        query: str,
        content_type: str = "pageBlogPost",
        limit: int = 10,
        order: str = "sys_publishedAt_DESC",
        search_fields: list[str] | None = None,
        author_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search blog posts from Contentful using advanced GraphQL filters.

        Args:
            query: Search query string
            content_type: Content type ID for blog posts
            limit: Maximum number of posts to return
            order: Sort order (default: newest first)
            search_fields: Fields to search in (default: ['title'])
            author_filter: Filter by author name (optional)

        Returns:
            List of matching blog post dictionaries
        """
        # Build where clause with advanced filters
        where_conditions = []

        # Default search fields if none specified
        if search_fields is None:
            search_fields = ["title"]

        # Add field-based search conditions
        field_conditions = []
        for field in search_fields:
            field_conditions.append(f'{field}_contains: "{query}"')

        # If multiple fields, use OR logic (we'll use separate queries for now)
        # For simplicity, we'll search title first, but this can be enhanced
        if "title" in search_fields:
            where_conditions.append(f'title_contains: "{query}"')

        # Add author filter if specified
        if author_filter:
            where_conditions.append(f'author: {{ name_contains: "{author_filter}" }}')

        # Build the where clause
        where_clause = (
            ", ".join(where_conditions) if where_conditions else 'title_contains: ""'
        )

        graphql_query = f"""
        query {{
            {content_type}Collection(
                limit: {limit},
                order: {order},
                where: {{
                    {where_clause}
                }}
            ) {{
                items {{
                    sys {{
                        id
                        publishedAt
                    }}
                    title
                    slug
                    content {{
                        json
                    }}
                    author {{
                        name
                    }}
                    publishedDate
                }}
            }}
        }}
        """

        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json={"query": graphql_query},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL search errors: {data['errors']}")
                return [
                    {
                        "title": f"Error searching Contentful for '{query}'",
                        "date": "",
                        "author": "",
                        "content": f"Search error: {data['errors']}",
                        "url": "",
                        "id": "",
                    }
                ]

            items = (
                data.get("data", {})
                .get(f"{content_type}Collection", {})
                .get("items", [])
            )

            posts = []
            for item in items:
                post_data = self._extract_graphql_post_data(item)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
            logger.error(f"Error searching Contentful GraphQL: {e}")
            return [
                {
                    "title": f"Error searching Contentful for '{query}'",
                    "date": "",
                    "author": "",
                    "content": f"Search error: {str(e)}",
                    "url": "",
                    "id": "",
                }
            ]

    def advanced_search_blog_posts(
        self,
        query: str,
        content_type: str = "pageBlogPost",
        limit: int = 10,
        order: str = "sys_publishedAt_DESC",
        **filters,
    ) -> list[dict[str, Any]]:
        """Advanced search with multiple filter options.

        Args:
            query: Main search query
            content_type: Content type ID
            limit: Maximum results
            order: Sort order
            **filters: Additional filters like author_name, title_exact, etc.

        Returns:
            List of matching blog post dictionaries
        """
        where_conditions = []

        # Main search query - search in title by default
        if query:
            where_conditions.append(f'title_contains: "{query}"')

        # Handle additional filters
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue

            if filter_key == "author_name":
                where_conditions.append(
                    f'author: {{ name_contains: "{filter_value}" }}'
                )
            elif filter_key == "title_exact":
                where_conditions.append(f'title: "{filter_value}"')
            elif filter_key == "title_in":
                if isinstance(filter_value, list):
                    title_list = ", ".join([f'"{t}"' for t in filter_value])
                    where_conditions.append(f"title_in: [{title_list}]")
            elif filter_key == "author_exists":
                where_conditions.append(f"author_exists: {str(filter_value).lower()}")
            elif filter_key == "published_after":
                where_conditions.append(f'publishedDate_gte: "{filter_value}"')
            elif filter_key == "published_before":
                where_conditions.append(f'publishedDate_lte: "{filter_value}"')

        # Build where clause
        where_clause = (
            ", ".join(where_conditions) if where_conditions else "title_exists: true"
        )

        graphql_query = f"""
        query {{
            {content_type}Collection(
                limit: {limit},
                order: {order},
                where: {{
                    {where_clause}
                }}
            ) {{
                items {{
                    sys {{
                        id
                        publishedAt
                    }}
                    title
                    slug
                    content {{
                        json
                    }}
                    author {{
                        name
                    }}
                    publishedDate
                }}
            }}
        }}
        """

        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json={"query": graphql_query},
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL advanced search errors: {data['errors']}")
                return [
                    {
                        "title": f"Error in advanced search for '{query}'",
                        "date": "",
                        "author": "",
                        "content": f"Search error: {data['errors']}",
                        "url": "",
                        "id": "",
                    }
                ]

            items = (
                data.get("data", {})
                .get(f"{content_type}Collection", {})
                .get("items", [])
            )

            posts = []
            for item in items:
                post_data = self._extract_graphql_post_data(item)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return [
                {
                    "title": f"Error in advanced search for '{query}'",
                    "date": "",
                    "author": "",
                    "content": f"Search error: {str(e)}",
                    "url": "",
                    "id": "",
                }
            ]


# Convenience function for easy usage
def fetch_contentful_posts(
    space_id: str | None = None,
    access_token: str | None = None,
    content_type: str = "pageBlogPost",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Convenience function to fetch blog posts from Contentful via GraphQL.

    Args:
        space_id: Contentful space ID
        access_token: Contentful access token
        content_type: Content type ID for blog posts
        limit: Maximum number of posts to fetch

    Returns:
        List of blog post dictionaries
    """
    client = ContentfulClient(space_id, access_token)
    return client.fetch_blog_posts(content_type, limit)
