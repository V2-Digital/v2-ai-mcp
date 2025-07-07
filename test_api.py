#!/usr/bin/env python3
"""
Test script to validate Contentful API integration and blog ingestion.
Run with: uv run python test_api.py
"""

import os
import sys
from typing import Any

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from v2_ai_mcp.contentful_client import (  # noqa: E402
    ContentfulClient,
    fetch_contentful_posts,
)
from v2_ai_mcp.scraper import fetch_blog_post, fetch_blog_posts  # noqa: E402
from v2_ai_mcp.summarizer import summarize  # noqa: E402


def test_contentful_connection():
    """Test basic Contentful API connection."""
    print("🔍 Testing Contentful Connection...")

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    if not space_id or not access_token:
        print("❌ Contentful credentials not found")
        print(
            "   Set CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN environment variables"
        )
        return False

    try:
        ContentfulClient(space_id, access_token)
        print(f"✅ Connected to Contentful space: {space_id}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_fetch_contentful_posts():
    """Test fetching blog posts from Contentful."""
    print("\n📚 Testing Contentful Blog Post Fetching...")

    try:
        content_type = os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost")
        posts = fetch_contentful_posts(content_type=content_type, limit=5)

        print(f"✅ Fetched {len(posts)} posts from Contentful")

        for i, post in enumerate(posts[:3]):  # Show first 3
            print(f"\n   📝 Post {i+1}:")
            print(f"      Title: {post.get('title', 'No title')[:60]}...")
            print(f"      Author: {post.get('author', 'No author')}")
            print(f"      Date: {post.get('date', 'No date')}")
            print(f"      Content: {len(post.get('content', ''))} characters")
            print(f"      ID: {post.get('id', 'No ID')}")

        return posts

    except Exception as e:
        print(f"❌ Failed to fetch posts: {e}")
        return []


def test_v2ai_fallback():
    """Test V2.ai scraping fallback."""
    print("\n🌐 Testing V2.ai Scraping Fallback...")

    try:
        url = "https://www.v2.ai/insights/adopting-AI-assistants-while-balancing-risks"
        post = fetch_blog_post(url)

        print("✅ Scraped V2.ai post successfully")
        print(f"   Title: {post.get('title', 'No title')[:60]}...")
        print(f"   Author: {post.get('author', 'No author')}")
        print(f"   Date: {post.get('date', 'No date')}")
        print(f"   Content: {len(post.get('content', ''))} characters")

        return post

    except Exception as e:
        print(f"❌ Failed to scrape V2.ai: {e}")
        return {}


def test_unified_fetch():
    """Test the unified fetch_blog_posts function."""
    print("\n🔄 Testing Unified Blog Post Fetching...")

    try:
        posts = fetch_blog_posts()

        print(f"✅ Unified fetch returned {len(posts)} posts")

        # Determine source
        has_contentful = os.getenv("CONTENTFUL_SPACE_ID") and os.getenv(
            "CONTENTFUL_ACCESS_TOKEN"
        )
        source = "Contentful" if has_contentful and len(posts) > 1 else "V2.ai scraping"
        print(f"   Source: {source}")

        for i, post in enumerate(posts[:2]):  # Show first 2
            print(f"\n   📄 Post {i+1}:")
            print(f"      Title: {post.get('title', 'No title')[:50]}...")
            print(f"      Author: {post.get('author', 'No author')}")
            print(f"      Date: {post.get('date', 'No date')}")

        return posts

    except Exception as e:
        print(f"❌ Unified fetch failed: {e}")
        return []


def test_summarization(posts: list[dict[str, Any]]):
    """Test AI summarization on fetched posts."""
    print("\n🤖 Testing AI Summarization...")

    if not posts:
        print("❌ No posts available for summarization")
        return

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OpenAI API key not found")
        print("   Set OPENAI_API_KEY environment variable")
        return

    try:
        post = posts[0]  # Test with first post
        content = post.get("content", "")

        if not content or content == "No content":
            print("❌ No content available for summarization")
            return

        # Use first 1000 characters for testing
        test_content = content[:1000]
        summary = summarize(test_content)

        print("✅ Generated summary successfully")
        print(f"   Original: {len(content)} characters")
        print(f"   Test chunk: {len(test_content)} characters")
        print(f"   Summary: {summary[:200]}...")

    except Exception as e:
        print(f"❌ Summarization failed: {e}")


def test_contentful_search():
    """Test Contentful search functionality."""
    print("\n🔍 Testing Contentful Search...")

    try:
        from v2_ai_mcp.contentful_client import ContentfulClient

        space_id = os.getenv("CONTENTFUL_SPACE_ID")
        access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

        if not space_id or not access_token:
            print("❌ Contentful credentials not found for search test")
            return

        client = ContentfulClient(space_id, access_token)
        content_type = os.getenv("CONTENTFUL_CONTENT_TYPE", "blogPost")

        # Test search queries
        search_queries = ["AI", "automation", "security", "risk"]

        for query in search_queries:
            try:
                results = client.search_blog_posts(
                    query, content_type=content_type, limit=3
                )
                print(f"✅ Search '{query}': {len(results)} results")

                for i, post in enumerate(results[:2]):  # Show first 2 results
                    print(
                        f"   📄 Result {i+1}: {post.get('title', 'No title')[:50]}..."
                    )

            except Exception as e:
                print(f"❌ Search '{query}' failed: {e}")

    except Exception as e:
        print(f"❌ Search test failed: {e}")


def test_mcp_tools_simulation():
    """Simulate MCP tool calls."""
    print("\n🛠️  Testing MCP Tools Simulation...")

    try:
        # Simulate get_latest_posts()
        posts = fetch_blog_posts()
        print(f"✅ get_latest_posts(): {len(posts)} posts")

        # Simulate get_post_content(0)
        if posts:
            post_content = posts[0]
            print(
                f"✅ get_post_content(0): {post_content.get('title', 'No title')[:40]}..."
            )

        # Simulate summarize_post(0)
        if posts and os.getenv("OPENAI_API_KEY"):
            try:
                content = posts[0].get("content", "")[:500]  # Short test
                summarize(content)
                print("✅ summarize_post(0): Generated summary")
            except Exception as e:
                print(f"⚠️  summarize_post(0): {e}")

        # Simulate search_blogs()
        if os.getenv("CONTENTFUL_SPACE_ID") and os.getenv("CONTENTFUL_ACCESS_TOKEN"):
            try:
                from v2_ai_mcp.contentful_client import ContentfulClient

                client = ContentfulClient()
                search_results = client.search_blog_posts("AI", limit=2)
                print(f"✅ search_blogs('AI'): {len(search_results)} results")
            except Exception as e:
                print(f"⚠️  search_blogs('AI'): {e}")

    except Exception as e:
        print(f"❌ MCP tools simulation failed: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting API Validation Tests\n")
    print("=" * 50)

    # Test Contentful connection
    contentful_works = test_contentful_connection()

    # Test Contentful fetching
    contentful_posts = []
    if contentful_works:
        contentful_posts = test_fetch_contentful_posts()

    # Test V2.ai fallback
    v2ai_post = test_v2ai_fallback()

    # Test unified fetching
    unified_posts = test_unified_fetch()

    # Test summarization
    test_posts = (
        contentful_posts if contentful_posts else ([v2ai_post] if v2ai_post else [])
    )
    if test_posts:
        test_summarization(test_posts)

    # Test search functionality
    if contentful_works:
        test_contentful_search()

    # Test MCP tools
    test_mcp_tools_simulation()

    print("\n" + "=" * 50)
    print("🏁 Tests Complete!")

    # Summary
    print("\n📊 Summary:")
    print(f"   Contentful: {'✅ Working' if contentful_works else '❌ Not configured'}")
    print(f"   V2.ai Scraping: {'✅ Working' if v2ai_post else '❌ Failed'}")
    print(f"   Unified Fetch: {'✅ Working' if unified_posts else '❌ Failed'}")
    print(
        f"   OpenAI API: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Not configured'}"
    )


if __name__ == "__main__":
    main()
