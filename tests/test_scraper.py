"""Unit tests for the scraper module."""

import pytest
import responses
from unittest.mock import patch
from src.v2_ai_mcp.scraper import fetch_blog_post, fetch_blog_posts


@responses.activate
def test_fetch_blog_post_success():
    """Test successful blog post fetching."""
    test_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Blog Post Title</h1>
            <div>
                <p>This is the first paragraph of content.</p>
                <p>This is the second paragraph of content.</p>
            </div>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com/test-post",
        body=test_html,
        status=200,
        content_type="text/html"
    )
    
    result = fetch_blog_post("https://example.com/test-post")
    
    assert result["title"] == "Test Blog Post Title"
    assert result["author"] == "Ashley Rodan"  # Hard-coded for V2.ai
    assert result["url"] == "https://example.com/test-post"
    assert "first paragraph" in result["content"]
    assert "second paragraph" in result["content"]


@responses.activate
def test_fetch_blog_post_with_date():
    """Test blog post fetching with date extraction."""
    test_html = """
    <html>
        <body>
            <h1>Test Post</h1>
            <div>
                <p>Ashley RodanJuly 15, 2024</p>
                <p>Content paragraph.</p>
            </div>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com/date-test",
        body=test_html,
        status=200,
        content_type="text/html"
    )
    
    result = fetch_blog_post("https://example.com/date-test")
    
    assert result["title"] == "Test Post"
    assert result["date"] == "July 15, 2024"
    assert result["author"] == "Ashley Rodan"


@responses.activate
def test_fetch_blog_post_request_error():
    """Test handling of request errors."""
    responses.add(
        responses.GET,
        "https://example.com/error",
        status=404
    )
    
    result = fetch_blog_post("https://example.com/error")
    
    assert result["title"] == "Error fetching post"
    assert "Error:" in result["content"]
    assert result["url"] == "https://example.com/error"


@responses.activate
def test_fetch_blog_post_no_content():
    """Test handling of pages with no content."""
    test_html = """
    <html>
        <head><title>Empty Page</title></head>
        <body>
            <h1>Empty Post</h1>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com/empty",
        body=test_html,
        status=200,
        content_type="text/html"
    )
    
    result = fetch_blog_post("https://example.com/empty")
    
    assert result["title"] == "Empty Post"
    assert result["content"] == "Content not found"


@responses.activate
def test_fetch_blog_post_date_cleaning():
    """Test date extraction and cleaning functionality."""
    test_html = """
    <html>
        <body>
            <h1>Test Post</h1>
            <div>
                <p>Some text Ashley RodanDecember 25, 2024 more text</p>
                <p>Content here.</p>
            </div>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com/date-clean",
        body=test_html,
        status=200,
        content_type="text/html"
    )
    
    result = fetch_blog_post("https://example.com/date-clean")
    
    assert result["date"] == "December 25, 2024"
    assert "Rodan" not in result["date"]


@responses.activate
def test_fetch_blog_post_fallback_content():
    """Test fallback content extraction when main selectors fail."""
    test_html = """
    <html>
        <body>
            <h1>Fallback Test</h1>
            <script>console.log('remove me');</script>
            <style>.hidden { display: none; }</style>
            <p>First paragraph</p>
            <p>Second paragraph</p>
            <p></p>
            <p>Third paragraph with content</p>
        </body>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com/fallback",
        body=test_html,
        status=200,
        content_type="text/html"
    )
    
    result = fetch_blog_post("https://example.com/fallback")
    
    assert "First paragraph" in result["content"]
    assert "Second paragraph" in result["content"] 
    assert "Third paragraph with content" in result["content"]
    assert "console.log" not in result["content"]
    assert ".hidden" not in result["content"]


@responses.activate
def test_fetch_blog_post_various_date_formats():
    """Test different date format extraction."""
    test_cases = [
        ("July 15, 2024", "July 15, 2024"),
        ("15 July 2024", "15 July 2024"),
        ("07/15/2024", "07/15/2024"),
        ("2024-07-15", "2024-07-15")
    ]
    
    for i, (date_in_html, expected_date) in enumerate(test_cases):
        test_html = f"""
        <html>
            <body>
                <h1>Date Test {i}</h1>
                <div>
                    <p>Published on {date_in_html}</p>
                    <p>Content here.</p>
                </div>
            </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            f"https://example.com/date-test-{i}",
            body=test_html,
            status=200,
            content_type="text/html"
        )
        
        result = fetch_blog_post(f"https://example.com/date-test-{i}")
        assert result["date"] == expected_date


def test_fetch_blog_posts():
    """Test the main fetch_blog_posts function."""
    with patch('src.v2_ai_mcp.scraper.fetch_blog_post') as mock_fetch:
        mock_fetch.return_value = {
            "title": "Test Post",
            "author": "Ashley Rodan",
            "date": "July 3, 2025",
            "content": "Test content",
            "url": "https://www.v2.ai/insights/adopting-AI-assistants-while-balancing-risks"
        }
        
        result = fetch_blog_posts()
        
        assert len(result) == 1
        assert result[0]["title"] == "Test Post"
        assert result[0]["author"] == "Ashley Rodan"
        mock_fetch.assert_called_once_with(
            "https://www.v2.ai/insights/adopting-AI-assistants-while-balancing-risks"
        )