📄 Product Requirements Document (PRD)
Project Title: V2.ai Insights Scraper MCP
gofastmcp.com
+5
gofastmcp.com
+5
scrapegraphai.com
+5
🧭 Overview
Objective: Develop a local MCP server in Python using FastMCP that scrapes blog posts from V2.ai Insights, extracts relevant information (title, date, author, content), summarizes the content using OpenAI's GPT-4, and integrates with Claude Desktop for enhanced AI interactions.

🎯 Goals
Implement a local MCP server using FastMCP.

Scrape blog posts from V2.ai Insights.

Extract the following data from each post:

Title

Publication Date

Author

Content

Summarize the content using OpenAI's GPT-4 API.

Expose tools via MCP for:

Retrieving the latest blog posts.

Summarizing a specific blog post by index.

Ensure compatibility and integration with Claude Desktop.
mcp.so

📦 Features
1. MCP Server Implementation
Utilize FastMCP to create a local MCP server.

Define tools using decorators for easy integration.
thewindowsclub.com
gofastmcp.com
+2
mcp.so
+2
composio.dev
+2

2. Web Scraping
Use requests to fetch HTML content from V2.ai Insights.

Parse HTML using BeautifulSoup to extract required data.
firecrawl.dev

3. Content Summarization
Integrate OpenAI's GPT-4 API to generate summaries of blog post content.

Handle API responses and errors gracefully.

4. Claude Desktop Integration
Ensure the MCP server is accessible and compatible with Claude Desktop.

Provide clear instructions for integration.
thewindowsclub.com
+3
github.com
+3
jheiduk.com
+3

🛠️ Technical Specifications
Programming Language:
Python 3.8+

Libraries and Frameworks:
FastMCP

BeautifulSoup4

Requests

OpenAI Python SDK

Directory Structure:
plaintext
Copy
Edit
v2ai_insights_scraper/
├── main.py
├── scraper.py
├── summarizer.py
├── requirements.txt
└── README.md
Tools Exposed via MCP:
get_latest_posts: Retrieves the latest blog posts with metadata.

summarize_post(index: int): Returns a summary of the blog post at the specified index.

🚀 Implementation Plan
Step 1: Environment Setup
Create a virtual environment:

bash
Copy
Edit
  python3 -m venv venv
  source venv/bin/activate
Install dependencies:

bash
Copy
Edit
  pip install fastmcp beautifulsoup4 requests openai
Generate requirements.txt:

bash
Copy
Edit
  pip freeze > requirements.txt
github.com
+6
github.com
+6
danielecer.com
+6

Step 2: Web Scraper (scraper.py)
Implement fetch_blog_posts() function to:

Send a GET request to V2.ai Insights.

Parse the HTML content using BeautifulSoup.

Extract title, date, author, and content for each blog post.

Return a list of dictionaries containing the extracted data.

Step 3: Summarizer (summarizer.py)
Implement summarize(text: str) -> str function to:

Send the text to OpenAI's GPT-4 API for summarization.

Handle the API response and extract the summary.

Return the summarized text.

Step 4: MCP Server (main.py)
Initialize the FastMCP server:

python
Copy
Edit
  from fastmcp import FastMCP
  mcp = FastMCP("V2 Insights Scraper")
Define tools using decorators:

python
Copy
Edit
  @mcp.tool
  def get_latest_posts():
      return fetch_blog_posts()

  @mcp.tool
  def summarize_post(index: int):
      posts = fetch_blog_posts()
      if 0 <= index < len(posts):
          return summarize(posts[index]["content"])
      else:
          return "Invalid index."
Run the MCP server:

python
Copy
Edit
  if __name__ == "__main__":
      mcp.run()
github.com
+2
mcp.so
+2
composio.dev
+2

Step 5: Claude Desktop Integration
Ensure Claude Desktop is installed and configured.

Start the MCP server locally.

In Claude Desktop, add the MCP server as a new tool:

Navigate to settings or tools integration section.

Provide the local server address (e.g., http://localhost:8000).

Test the connection and ensure tools are accessible.

📚 Resources
FastMCP Documentation: https://gofastmcp.com/getting-started/welcome

FastMCP GitHub Repository: https://github.com/jlowin/fastmcp

OpenAI API Documentation: https://platform.openai.com/docs

BeautifulSoup Documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

Requests Library Documentation: https://docs.python-requests.org/en/latest/

✅ Acceptance Criteria
The MCP server runs locally without errors.

get_latest_posts returns a list of blog posts with title, date, author, and content.

summarize_post(index) returns a coherent summary of the specified blog post.

Claude Desktop successfully integrates with the MCP server and can invoke the defined tools.

📝 Notes
Ensure that the OpenAI API key is securely stored and not hard-coded.

Implement error handling for network requests and API calls.

Consider adding caching mechanisms to avoid redundant API calls for summarization.

Future enhancements may include scheduling periodic scraping and storing data in a local database.

This PRD serves as a blueprint for your project. You can now proceed to implement each component as outlined. If you need further assistance or code examples for any of the steps, feel free to ask!
