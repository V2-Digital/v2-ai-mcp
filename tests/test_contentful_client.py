"""Unit tests for the contentful_client module."""

import os
from unittest.mock import Mock, patch

import pytest

from src.v2_ai_mcp.contentful_client import (
    ContentfulClient,
    fetch_contentful_posts,
)


class TestContentfulClient:
    """Test cases for ContentfulClient class."""

    def test_init_with_params(self):
        """Test initialization with provided parameters."""
        with patch("src.v2_ai_mcp.contentful_client.contentful.Client") as mock_client:
            client = ContentfulClient("test_space", "test_token", "staging")

            assert client.space_id == "test_space"
            assert client.access_token == "test_token"
            assert client.environment == "staging"
            mock_client.assert_called_once_with(
                space_id="test_space",
                access_token="test_token",
                environment="staging",
            )

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch("src.v2_ai_mcp.contentful_client.contentful.Client") as mock_client:
            with patch.dict(
                os.environ,
                {
                    "CONTENTFUL_SPACE_ID": "env_space",
                    "CONTENTFUL_ACCESS_TOKEN": "env_token",
                },
            ):
                client = ContentfulClient()

                assert client.space_id == "env_space"
                assert client.access_token == "env_token"
                assert client.environment == "master"
                mock_client.assert_called_once_with(
                    space_id="env_space",
                    access_token="env_token",
                    environment="master",
                )

    def test_init_missing_credentials(self):
        """Test initialization fails with missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="space_id and access_token are required"
            ):
                ContentfulClient()

    def test_init_missing_space_id(self):
        """Test initialization fails with missing space ID."""
        with patch.dict(os.environ, {"CONTENTFUL_ACCESS_TOKEN": "token"}, clear=True):
            with pytest.raises(
                ValueError, match="space_id and access_token are required"
            ):
                ContentfulClient()

    def test_init_missing_access_token(self):
        """Test initialization fails with missing access token."""
        with patch.dict(os.environ, {"CONTENTFUL_SPACE_ID": "space"}, clear=True):
            with pytest.raises(
                ValueError, match="space_id and access_token are required"
            ):
                ContentfulClient()

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_fetch_blog_posts_success(self, mock_client_class):
        """Test successful blog posts fetching."""
        # Mock Contentful client and entries
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create mock entry
        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Test Blog Post",
            "content": "Test content",
            "author": "Test Author",
            "slug": "test-post",
        }
        mock_entry.sys = {"id": "test123", "createdAt": "2024-01-01T00:00:00Z"}

        mock_client.entries.return_value = [mock_entry]

        client = ContentfulClient("space", "token")
        posts = client.fetch_blog_posts("blogPost", 5, "-sys.createdAt")

        # Verify API call
        mock_client.entries.assert_called_once_with(
            {
                "content_type": "blogPost",
                "limit": 5,
                "order": "-sys.createdAt",
            }
        )

        # Verify result
        assert len(posts) == 1
        assert posts[0]["title"] == "Test Blog Post"
        assert posts[0]["author"] == "Test Author"
        assert posts[0]["content"] == "Test content"
        assert posts[0]["id"] == "test123"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_fetch_blog_posts_error(self, mock_client_class):
        """Test blog posts fetching with error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.entries.side_effect = Exception("API Error")

        client = ContentfulClient("space", "token")
        posts = client.fetch_blog_posts()

        # Should return error post
        assert len(posts) == 1
        assert posts[0]["title"] == "Error fetching from Contentful"
        assert "API Error" in posts[0]["content"]

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_fetch_single_post_success(self, mock_client_class):
        """Test successful single post fetching."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Single Post",
            "content": "Single content",
        }
        mock_entry.sys = {"id": "single123"}

        mock_client.entry.return_value = mock_entry

        client = ContentfulClient("space", "token")
        post = client.fetch_single_post("single123")

        mock_client.entry.assert_called_once_with("single123")
        assert post["title"] == "Single Post"
        assert post["id"] == "single123"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_fetch_single_post_error(self, mock_client_class):
        """Test single post fetching with error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.entry.side_effect = Exception("Entry not found")

        client = ContentfulClient("space", "token")
        post = client.fetch_single_post("invalid123")

        assert post["title"] == "Error fetching post"
        assert "Entry not found" in post["content"]
        assert post["id"] == "invalid123"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_search_blog_posts_success(self, mock_client_class):
        """Test successful blog posts search."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "AI Blog Post",
            "content": "Content about artificial intelligence",
        }
        mock_entry.sys = {"id": "ai123"}

        mock_client.entries.return_value = [mock_entry]

        client = ContentfulClient("space", "token")
        posts = client.search_blog_posts("AI", "blogPost", 3)

        mock_client.entries.assert_called_once_with(
            {
                "content_type": "blogPost",
                "query": "AI",
                "limit": 3,
                "order": "-sys.createdAt",
            }
        )

        assert len(posts) == 1
        assert posts[0]["title"] == "AI Blog Post"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_search_blog_posts_error(self, mock_client_class):
        """Test blog posts search with error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.entries.side_effect = Exception("Search failed")

        client = ContentfulClient("space", "token")
        posts = client.search_blog_posts("test query")

        assert len(posts) == 1
        assert "Error searching Contentful for 'test query'" in posts[0]["title"]
        assert "Search failed" in posts[0]["content"]


class TestContentExtractionMethods:
    """Test cases for content extraction methods."""

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_complete(self, mock_client_class):
        """Test post data extraction with complete data."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Create mock entry with complete data
        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Complete Post",
            "content": "Full content here",
            "author": "John Doe",
            "slug": "complete-post",
        }
        mock_entry.sys = {"id": "complete123", "createdAt": "2024-01-01"}

        result = client._extract_post_data(mock_entry)

        assert result["title"] == "Complete Post"
        assert result["content"] == "Full content here"
        assert result["author"] == "John Doe"
        assert result["url"] == "https://your-site.com/complete-post"
        assert result["id"] == "complete123"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_minimal(self, mock_client_class):
        """Test post data extraction with minimal data."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_entry = Mock()
        mock_entry.fields.return_value = {}
        mock_entry.sys = {}

        result = client._extract_post_data(mock_entry)

        assert result["title"] == "No title"
        assert result["content"] == "No content"
        assert result["author"] == "Unknown Author"
        assert result["url"] == ""

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_error(self, mock_client_class):
        """Test post data extraction with error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_entry = Mock()
        mock_entry.fields.side_effect = Exception("Field access error")

        with patch("builtins.print"):  # Suppress print output during test
            result = client._extract_post_data(mock_entry)

        assert result is None

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_linked_entry(self, mock_client_class):
        """Test author extraction from linked entry."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Mock linked author entry
        mock_author = Mock()
        mock_author.fields.return_value = {"name": "Jane Smith"}

        fields = {"author": mock_author}
        result = client._extract_author(fields)

        assert result == "Jane Smith"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_list(self, mock_client_class):
        """Test author extraction from author list."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_author = Mock()
        mock_author.fields.return_value = {"fullName": "Bob Johnson"}

        fields = {"author": [mock_author]}
        result = client._extract_author(fields)

        assert result == "Bob Johnson"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_string(self, mock_client_class):
        """Test author extraction from string value."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {"authorName": "Direct Author"}
        result = client._extract_author(fields)

        assert result == "Direct Author"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_fallback(self, mock_client_class):
        """Test author extraction fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {}
        result = client._extract_author(fields)

        assert result == "Unknown Author"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_date_datetime_object(self, mock_client_class):
        """Test date extraction from datetime object."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_date = Mock()
        mock_date.isoformat.return_value = "2024-01-01T12:00:00Z"

        fields = {"publishDate": mock_date}
        mock_entry = Mock()

        result = client._extract_date(fields, mock_entry)

        assert result == "2024-01-01T12:00:00Z"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_date_string(self, mock_client_class):
        """Test date extraction from string."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {"date": "2024-01-01"}
        mock_entry = Mock()

        result = client._extract_date(fields, mock_entry)

        assert result == "2024-01-01"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_date_fallback_sys(self, mock_client_class):
        """Test date extraction fallback to sys.createdAt."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {}
        mock_entry = Mock()
        mock_entry.sys = {"createdAt": "2024-01-01T00:00:00Z"}

        result = client._extract_date(fields, mock_entry)

        assert result == "2024-01-01T00:00:00Z"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_date_no_date(self, mock_client_class):
        """Test date extraction with no date available."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {}
        mock_entry = Mock()
        mock_entry.sys = {}

        result = client._extract_date(fields, mock_entry)

        assert result == "No date available"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_rich_text_success(self, mock_client_class):
        """Test rich text extraction success."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Mock rich text structure
        mock_text_node = Mock()
        mock_text_node.value = "First paragraph"

        mock_text_node2 = Mock()
        mock_text_node2.value = "Second paragraph"

        mock_paragraph1 = Mock()
        mock_paragraph1.content = [mock_text_node]

        mock_paragraph2 = Mock()
        mock_paragraph2.content = [mock_text_node2]

        mock_rich_text = Mock()
        mock_rich_text.content = [mock_paragraph1, mock_paragraph2]

        result = client._extract_rich_text(mock_rich_text)

        assert result == "First paragraph\n\nSecond paragraph"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_rich_text_fallback(self, mock_client_class):
        """Test rich text extraction fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        simple_text = "Simple text content"
        result = client._extract_rich_text(simple_text)

        assert result == "Simple text content"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_rich_text_error(self, mock_client_class):
        """Test rich text extraction with error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_rich_text = Mock()
        mock_rich_text.content = None  # This will cause AttributeError

        result = client._extract_rich_text(mock_rich_text)

        # Should fallback to string representation
        assert result == str(mock_rich_text)


class TestConvenienceFunction:
    """Test cases for convenience functions."""

    @patch("src.v2_ai_mcp.contentful_client.ContentfulClient")
    def test_fetch_contentful_posts_with_params(self, mock_client_class):
        """Test convenience function with parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.fetch_blog_posts.return_value = [{"title": "Test Post"}]

        result = fetch_contentful_posts("space", "token", "customType", 5)

        mock_client_class.assert_called_once_with("space", "token")
        mock_client.fetch_blog_posts.assert_called_once_with("customType", 5)
        assert result == [{"title": "Test Post"}]

    @patch("src.v2_ai_mcp.contentful_client.ContentfulClient")
    def test_fetch_contentful_posts_defaults(self, mock_client_class):
        """Test convenience function with defaults."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.fetch_blog_posts.return_value = []

        result = fetch_contentful_posts()

        mock_client_class.assert_called_once_with(None, None)
        mock_client.fetch_blog_posts.assert_called_once_with("blogPost", 10)
        assert result == []


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_error_handling(self, mock_client_class):
        """Test author extraction with various error conditions."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Mock author with failing fields() method
        mock_author = Mock()
        mock_author.fields.side_effect = Exception("Field error")

        fields = {"author": mock_author}
        result = client._extract_author(fields)

        # Should fallback to Unknown Author
        assert result == "Unknown Author"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_empty_list(self, mock_client_class):
        """Test author extraction with empty author list."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {"author": []}
        result = client._extract_author(fields)

        # Empty list falls through to "other types" and gets stringified
        assert result == "[]"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_with_rich_text(self, mock_client_class):
        """Test post data extraction with rich text content."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Mock rich text content
        mock_content = Mock()
        mock_content.content = []  # Rich text object

        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Rich Text Post",
            "content": mock_content,
        }
        mock_entry.sys = {"id": "rich123"}

        with patch.object(
            client, "_extract_rich_text", return_value="Extracted text"
        ) as mock_extract:
            result = client._extract_post_data(mock_entry)

            mock_extract.assert_called_once_with(mock_content)
            assert result["content"] == "Extracted text"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_non_string_content(self, mock_client_class):
        """Test post data extraction with non-string content."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Number Content Post",
            "content": 12345,  # Non-string content
        }
        mock_entry.sys = {"id": "num123"}

        result = client._extract_post_data(mock_entry)

        assert result["content"] == "12345"  # Should be converted to string

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_with_body_field(self, mock_client_class):
        """Test post data extraction using 'body' field when 'content' not available."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_entry = Mock()
        mock_entry.fields.return_value = {
            "title": "Body Field Post",
            "body": "Content from body field",  # Use body instead of content
        }
        mock_entry.sys = {"id": "body123"}

        result = client._extract_post_data(mock_entry)

        assert result["content"] == "Content from body field"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_post_data_with_sys_date_fallback(self, mock_client_class):
        """Test post data extraction with sys.createdAt fallback for date."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        mock_entry = Mock()
        mock_entry.fields.return_value = {"title": "Sys Date Post"}
        mock_entry.sys = {"id": "sys123", "createdAt": "2024-02-01T10:00:00Z"}

        result = client._extract_post_data(mock_entry)

        assert result["date"] == "2024-02-01T10:00:00Z"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_date_other_types(self, mock_client_class):
        """Test date extraction with other data types."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        fields = {"publishDate": 1640995200}  # Unix timestamp as number
        mock_entry = Mock()

        result = client._extract_date(fields, mock_entry)

        assert result == "1640995200"

    @patch("src.v2_ai_mcp.contentful_client.contentful.Client")
    def test_extract_author_exception_in_list_processing(self, mock_client_class):
        """Test author extraction with exception in list processing."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        client = ContentfulClient("space", "token")

        # Mock author list with error-prone first author
        mock_author = Mock()
        mock_author.fields.side_effect = Exception("Author field error")

        fields = {"author": [mock_author]}
        result = client._extract_author(fields)

        # Should fallback to Unknown Author since exception is caught
        assert result == "Unknown Author"
