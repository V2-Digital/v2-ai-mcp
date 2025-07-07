from fastmcp import FastMCP
from scraper import fetch_blog_posts
from summarizer import summarize

# Initialize FastMCP server
mcp = FastMCP("V2 Insights Scraper")

@mcp.tool()
def get_latest_posts():
    """Retrieves the latest blog posts with metadata"""
    return fetch_blog_posts()

@mcp.tool()
def summarize_post(index: int):
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
            "summary": summary
        }
    else:
        return {"error": f"Invalid index. Available posts: 0 to {len(posts) - 1}"}

@mcp.tool()
def get_post_content(index: int):
    """Returns the full content of the blog post at the specified index"""
    posts = fetch_blog_posts()
    if 0 <= index < len(posts):
        return posts[index]
    else:
        return {"error": f"Invalid index. Available posts: 0 to {len(posts) - 1}"}

if __name__ == "__main__":
    mcp.run()