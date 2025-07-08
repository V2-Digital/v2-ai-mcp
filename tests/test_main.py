"""Unit tests for the main MCP server module."""

from unittest.mock import patch

from src.v2_ai_mcp.main import (
    _get_latest_posts,
    _get_post_content,
    _summarize_post,
    mcp,
)


def test_get_latest_posts():
    """Test the get_latest_posts function."""
    with patch("src.v2_ai_mcp.main._get_contentful_posts") as mock_fetch:
        mock_posts = [
            {
                "title": "Test Post",
                "author": "Ashley Rodan",
                "date": "July 3, 2025",
                "content": "Test content",
                "url": "https://example.com/test",
            }
        ]
        mock_fetch.return_value = mock_posts

        result = _get_latest_posts()

        assert result == mock_posts
        mock_fetch.assert_called_once_with(10)


def test_summarize_post_valid_id():
    """Test summarize_post with valid post ID."""
    mock_post = {
        "title": "Test Post",
        "author": "Ashley Rodan",
        "date": "July 3, 2025",
        "content": "This is test content for summarization.",
        "url": "https://example.com/test",
    }

    with (
        patch("src.v2_ai_mcp.main.ContentfulClient") as mock_client_class,
        patch("src.v2_ai_mcp.main.summarize") as mock_summarize,
        patch("src.v2_ai_mcp.main.os.getenv") as mock_getenv,
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "CONTENTFUL_SPACE_ID": "test_space",
            "CONTENTFUL_ACCESS_TOKEN": "test_token",
            "CONTENTFUL_CONTENT_TYPE": "blogPost",
        }.get(key, default)

        mock_client = mock_client_class.return_value
        mock_client.fetch_single_post.return_value = mock_post
        mock_summarize.return_value = "This is a test summary."

        result = _summarize_post("test_id")

        expected = {
            "title": "Test Post",
            "date": "July 3, 2025",
            "author": "Ashley Rodan",
            "url": "https://example.com/test",
            "summary": "This is a test summary.",
        }

        assert result == expected
        mock_client.fetch_single_post.assert_called_once_with(
            "test_id", content_type="blogPost"
        )
        mock_summarize.assert_called_once_with(
            "This is test content for summarization."
        )


def test_summarize_post_no_contentful_config():
    """Test summarize_post with no Contentful configuration."""
    with patch("src.v2_ai_mcp.main.os.getenv") as mock_getenv:
        mock_getenv.return_value = None

        result = _summarize_post("test_id")

        assert result == {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }


def test_summarize_post_with_error_content():
    """Test summarize_post when post content contains error."""
    mock_post = {
        "title": "Error Post",
        "content": "error: Post not found",  # lowercase 'error' to match the check
        "date": "",
        "author": "",
        "url": "",
    }

    with (
        patch("src.v2_ai_mcp.main.ContentfulClient") as mock_client_class,
        patch("src.v2_ai_mcp.main.os.getenv") as mock_getenv,
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "CONTENTFUL_SPACE_ID": "test_space",
            "CONTENTFUL_ACCESS_TOKEN": "test_token",
            "CONTENTFUL_CONTENT_TYPE": "blogPost",
        }.get(key, default)

        mock_client = mock_client_class.return_value
        mock_client.fetch_single_post.return_value = mock_post

        result = _summarize_post("test_id")

        assert result == mock_post


def test_get_post_content_valid_id():
    """Test get_post_content with valid post ID."""
    mock_post = {
        "title": "Test Post",
        "author": "Ashley Rodan",
        "date": "July 3, 2025",
        "content": "Full content here",
        "url": "https://example.com/test",
    }

    with (
        patch("src.v2_ai_mcp.main.ContentfulClient") as mock_client_class,
        patch("src.v2_ai_mcp.main.os.getenv") as mock_getenv,
    ):
        mock_getenv.side_effect = lambda key, default=None: {
            "CONTENTFUL_SPACE_ID": "test_space",
            "CONTENTFUL_ACCESS_TOKEN": "test_token",
            "CONTENTFUL_CONTENT_TYPE": "blogPost",
        }.get(key, default)

        mock_client = mock_client_class.return_value
        mock_client.fetch_single_post.return_value = mock_post

        result = _get_post_content("test_id")

        assert result == mock_post
        mock_client.fetch_single_post.assert_called_once_with(
            "test_id", content_type="blogPost"
        )


def test_get_post_content_no_contentful_config():
    """Test get_post_content with no Contentful configuration."""
    with patch("src.v2_ai_mcp.main.os.getenv") as mock_getenv:
        mock_getenv.return_value = None

        result = _get_post_content("test_id")

        assert result == {
            "error": "Contentful not configured. Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables."
        }


def test_mcp_server_initialization():
    """Test that MCP server is properly initialized."""
    assert mcp is not None
    assert hasattr(mcp, "run")


def test_tools_are_registered():
    """Test that MCP tools are properly registered."""
    # Test that private functions are available and callable
    assert callable(_get_latest_posts)
    assert callable(_summarize_post)
    assert callable(_get_post_content)

    # Test MCP server is initialized
    assert mcp is not None
    assert hasattr(mcp, "run")
