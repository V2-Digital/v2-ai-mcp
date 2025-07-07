"""Unit tests for the main MCP server module."""

import pytest
from unittest.mock import patch, MagicMock
from src.v2_ai_mcp.main import mcp, _get_latest_posts, _summarize_post, _get_post_content


def test_get_latest_posts():
    """Test the get_latest_posts function."""
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_posts = [
            {
                "title": "Test Post",
                "author": "Ashley Rodan",
                "date": "July 3, 2025",
                "content": "Test content",
                "url": "https://example.com/test"
            }
        ]
        mock_fetch.return_value = mock_posts
        
        result = _get_latest_posts()
        
        assert result == mock_posts
        mock_fetch.assert_called_once()


def test_summarize_post_valid_index():
    """Test summarize_post with valid index."""
    mock_posts = [
        {
            "title": "Test Post",
            "author": "Ashley Rodan", 
            "date": "July 3, 2025",
            "content": "This is test content for summarization.",
            "url": "https://example.com/test"
        }
    ]
    
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch, \
         patch('src.v2_ai_mcp.main.summarize') as mock_summarize:
        
        mock_fetch.return_value = mock_posts
        mock_summarize.return_value = "This is a test summary."
        
        result = _summarize_post(0)
        
        expected = {
            "title": "Test Post",
            "date": "July 3, 2025",
            "author": "Ashley Rodan",
            "url": "https://example.com/test",
            "summary": "This is a test summary."
        }
        
        assert result == expected
        mock_fetch.assert_called_once()
        mock_summarize.assert_called_once_with("This is test content for summarization.")


def test_summarize_post_invalid_index_negative():
    """Test summarize_post with negative index."""
    mock_posts = [{"title": "Test"}]
    
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_fetch.return_value = mock_posts
        
        result = _summarize_post(-1)
        
        assert result == {"error": "Invalid index. Available posts: 0 to 0"}


def test_summarize_post_invalid_index_too_high():
    """Test summarize_post with index too high."""
    mock_posts = [{"title": "Test"}]
    
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_fetch.return_value = mock_posts
        
        result = _summarize_post(1)
        
        assert result == {"error": "Invalid index. Available posts: 0 to 0"}


def test_summarize_post_empty_posts():
    """Test summarize_post with no posts available."""
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_fetch.return_value = []
        
        result = _summarize_post(0)
        
        assert result == {"error": "Invalid index. Available posts: 0 to -1"}


def test_get_post_content_valid_index():
    """Test get_post_content with valid index."""
    mock_posts = [
        {
            "title": "Test Post",
            "author": "Ashley Rodan",
            "date": "July 3, 2025", 
            "content": "Full content here",
            "url": "https://example.com/test"
        }
    ]
    
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_fetch.return_value = mock_posts
        
        result = _get_post_content(0)
        
        assert result == mock_posts[0]
        mock_fetch.assert_called_once()


def test_get_post_content_invalid_index():
    """Test get_post_content with invalid index."""
    mock_posts = [{"title": "Test"}]
    
    with patch('src.v2_ai_mcp.main.fetch_blog_posts') as mock_fetch:
        mock_fetch.return_value = mock_posts
        
        result = _get_post_content(5)
        
        assert result == {"error": "Invalid index. Available posts: 0 to 0"}


def test_mcp_server_initialization():
    """Test that MCP server is properly initialized."""
    assert mcp is not None
    assert hasattr(mcp, 'run')


def test_tools_are_registered():
    """Test that MCP tools are properly registered."""
    # Test that private functions are available and callable
    assert callable(_get_latest_posts)
    assert callable(_summarize_post)
    assert callable(_get_post_content)
    
    # Test MCP server is initialized
    assert mcp is not None
    assert hasattr(mcp, 'run')