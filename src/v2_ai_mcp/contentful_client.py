"""Contentful CMS integration for fetching blog posts."""

import os
from typing import Any

import contentful


class ContentfulClient:
    """Client for fetching content from Contentful CMS."""

    def __init__(
        self,
        space_id: str | None = None,
        access_token: str | None = None,
        environment: str = "master",
    ):
        """Initialize Contentful client.

        Args:
            space_id: Contentful space ID (or from CONTENTFUL_SPACE_ID env var)
            access_token: Contentful access token (or from CONTENTFUL_ACCESS_TOKEN env var)
            environment: Contentful environment (default: master)
        """
        self.space_id = space_id or os.getenv("CONTENTFUL_SPACE_ID")
        self.access_token = access_token or os.getenv("CONTENTFUL_ACCESS_TOKEN")
        self.environment = environment

        if not self.space_id or not self.access_token:
            raise ValueError(
                "Contentful space_id and access_token are required. "
                "Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
            )

        self.client = contentful.Client(
            space_id=self.space_id,
            access_token=self.access_token,
            environment=self.environment,
        )

    def fetch_blog_posts(
        self,
        content_type: str = "blogPost",
        limit: int = 10,
        order: str = "-sys.createdAt",
    ) -> list[dict[str, Any]]:
        """Fetch blog posts from Contentful.

        Args:
            content_type: Content type ID for blog posts
            limit: Maximum number of posts to fetch
            order: Sort order (default: newest first)

        Returns:
            List of blog post dictionaries
        """
        try:
            entries = self.client.entries(
                {
                    "content_type": content_type,
                    "limit": limit,
                    "order": order,
                }
            )

            posts = []
            for entry in entries:
                post_data = self._extract_post_data(entry)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
            return [
                {
                    "title": "Error fetching from Contentful",
                    "date": "",
                    "author": "",
                    "content": f"Error: {str(e)}",
                    "url": "",
                    "id": "",
                }
            ]

    def fetch_single_post(self, entry_id: str) -> dict[str, Any]:
        """Fetch a single blog post by entry ID.

        Args:
            entry_id: Contentful entry ID

        Returns:
            Blog post dictionary
        """
        try:
            entry = self.client.entry(entry_id)
            return self._extract_post_data(entry) or {
                "title": "Post not found",
                "date": "",
                "author": "",
                "content": "Post data could not be extracted",
                "url": "",
                "id": entry_id,
            }

        except Exception as e:
            return {
                "title": "Error fetching post",
                "date": "",
                "author": "",
                "content": f"Error: {str(e)}",
                "url": "",
                "id": entry_id,
            }

    def _extract_post_data(self, entry: Any) -> dict[str, Any] | None:
        """Extract blog post data from Contentful entry.

        Args:
            entry: Contentful entry object

        Returns:
            Extracted post data or None if extraction fails
        """
        try:
            fields = entry.fields()

            # Common field mappings - adjust based on your content model
            title = fields.get("title", "No title")
            content = fields.get("content", fields.get("body", "No content"))

            # Handle linked author entries
            author = self._extract_author(fields)

            # Handle date fields
            date = self._extract_date(fields, entry)

            if not date and hasattr(entry, "sys"):
                date = entry.sys.get("createdAt", "")

            # Handle slug/URL
            slug = fields.get("slug", "")
            url = f"https://your-site.com/{slug}" if slug else ""

            # Handle rich text content
            if hasattr(content, "content"):
                content = self._extract_rich_text(content)
            elif not isinstance(content, str):
                content = str(content)

            return {
                "title": str(title),
                "date": str(date),
                "author": str(author),
                "content": content,
                "url": url,
                "id": entry.sys.get("id", ""),
            }

        except Exception as e:
            print(f"Error extracting post data: {e}")
            return None

    def _extract_rich_text(self, rich_text: Any) -> str:
        """Extract plain text from Contentful rich text field.

        Args:
            rich_text: Rich text content object

        Returns:
            Plain text string
        """
        try:
            if hasattr(rich_text, "content") and isinstance(rich_text.content, list):
                text_parts = []
                for node in rich_text.content:
                    if hasattr(node, "content") and isinstance(node.content, list):
                        for text_node in node.content:
                            if hasattr(text_node, "value"):
                                text_parts.append(text_node.value)
                return "\n\n".join(text_parts)
            return str(rich_text)
        except Exception:
            return str(rich_text)

    def _extract_author(self, fields: dict[str, Any]) -> str:
        """Extract author name from various field types.

        Args:
            fields: Entry fields dictionary

        Returns:
            Author name string
        """
        # Try different author field names
        author_fields = ["author", "authorName", "writer", "createdBy"]

        for field_name in author_fields:
            if field_name in fields:
                author_value = fields[field_name]

                # Handle linked author entries
                if hasattr(author_value, "fields"):
                    try:
                        author_fields_data = author_value.fields()
                        # Try common name fields in author entries
                        name = (
                            author_fields_data.get("name")
                            or author_fields_data.get("fullName")
                            or author_fields_data.get("displayName")
                            or author_fields_data.get("title")
                            or "Unknown Author"
                        )
                        return str(name)
                    except Exception:
                        continue

                # Handle list of authors
                elif isinstance(author_value, list) and author_value:
                    first_author = author_value[0]
                    if hasattr(first_author, "fields"):
                        try:
                            author_fields_data = first_author.fields()
                            name = (
                                author_fields_data.get("name")
                                or author_fields_data.get("fullName")
                                or author_fields_data.get("displayName")
                                or author_fields_data.get("title")
                                or "Unknown Author"
                            )
                            return str(name)
                        except Exception:
                            continue
                    else:
                        return str(first_author)

                # Handle direct string values
                elif isinstance(author_value, str):
                    return author_value

                # Handle other types
                else:
                    return str(author_value)

        return "Unknown Author"

    def search_blog_posts(
        self,
        query: str,
        content_type: str = "blogPost",
        limit: int = 10,
        order: str = "-sys.createdAt",
    ) -> list[dict[str, Any]]:
        """Search blog posts from Contentful using text query.

        Args:
            query: Search query string
            content_type: Content type ID for blog posts
            limit: Maximum number of posts to return
            order: Sort order (default: newest first)

        Returns:
            List of matching blog post dictionaries
        """
        try:
            # Use Contentful's full-text search API
            entries = self.client.entries(
                {
                    "content_type": content_type,
                    "query": query,  # Full-text search across all fields
                    "limit": limit,
                    "order": order,
                }
            )

            posts = []
            for entry in entries:
                post_data = self._extract_post_data(entry)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
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

    def _extract_date(self, fields: dict[str, Any], entry: Any) -> str:
        """Extract publication date from various field types.

        Args:
            fields: Entry fields dictionary
            entry: Full entry object

        Returns:
            Date string
        """
        # Try different date field names
        date_fields = [
            "publishDate",
            "publicationDate",
            "publishedAt",
            "published",
            "date",
            "createdDate",
            "dateCreated",
            "createdAt",
        ]

        for field_name in date_fields:
            if field_name in fields:
                date_value = fields[field_name]

                # Handle datetime objects
                if hasattr(date_value, "isoformat"):
                    return str(date_value.isoformat())

                # Handle string dates
                elif isinstance(date_value, str) and date_value:
                    return date_value

                # Handle other types
                elif date_value:
                    return str(date_value)

        # Fallback to system creation date
        if hasattr(entry, "sys") and "createdAt" in entry.sys:
            return str(entry.sys["createdAt"])

        return "No date available"


# Convenience function for easy usage
def fetch_contentful_posts(
    space_id: str | None = None,
    access_token: str | None = None,
    content_type: str = "blogPost",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Convenience function to fetch blog posts from Contentful.

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
