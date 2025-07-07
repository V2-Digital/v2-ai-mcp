# V2.ai Insights Scraper MCP - Claude Assistant Instructions

## Project Overview
This is a Model Context Protocol (MCP) server that scrapes blog posts from V2.ai Insights, extracts content, and provides AI-powered summaries using OpenAI's GPT-4.

## Development Commands

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_scraper.py -v

# Run tests with coverage threshold check
uv run pytest --cov=src --cov-fail-under=60
```

### Code Quality
```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests

# Fix auto-fixable linting issues
uv run ruff check --fix src tests

# Type checking (if mypy is installed)
uv run mypy src
```

### Running the MCP Server
```bash
# Run the MCP server
uv run python -m src.v2_ai_mcp.main

# Test individual components
uv run python -c "from src.v2_ai_mcp.scraper import fetch_blog_posts; print(fetch_blog_posts()[0]['title'])"
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Update hook versions
uv run pre-commit autoupdate
```

## Project Structure
- `src/v2_ai_mcp/` - Main package source code
- `tests/` - Unit tests with 88%+ coverage
- `.github/workflows/` - CI/CD pipeline
- `pyproject.toml` - Project configuration and dependencies
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

## Key Files
- `main.py` - FastMCP server with 3 tools: get_latest_posts, summarize_post, get_post_content
- `scraper.py` - Web scraping logic for V2.ai blog posts
- `summarizer.py` - OpenAI GPT-4 integration for content summarization

## Environment Setup
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Set Contentful credentials (optional)
export CONTENTFUL_SPACE_ID="your-space-id"
export CONTENTFUL_ACCESS_TOKEN="your-access-token"

# Or create .env file with:
OPENAI_API_KEY=your-api-key-here
CONTENTFUL_SPACE_ID=your-contentful-space-id
CONTENTFUL_ACCESS_TOKEN=your-contentful-access-token
CONTENTFUL_CONTENT_TYPE=blogPost
```

## Claude Desktop Integration
The server integrates with Claude Desktop via MCP configuration in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "v2-insights-scraper": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/v2-ai-mcp", "python", "-m", "src.v2_ai_mcp.main"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Coverage Requirements
- Minimum test coverage: 60%
- Current coverage: 88%+
- CI pipeline fails if coverage drops below threshold

## Code Standards
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maintain test coverage above 60%
- All commits must pass pre-commit hooks
- All PRs must pass CI/CD pipeline

## Current Implementation
- Scrapes specific V2.ai blog post: "Adopting AI Assistants while Balancing Risks"
- Author: Ashley Rodan
- Successfully extracts title, date, author, and content (~12,785 characters)
- Provides AI summarization via OpenAI GPT-4

## Next Steps for Extension
- Add pagination support for multiple blog posts
- Implement caching for API responses
- Add configuration for different blog sources
- Enhance error handling and retry logic
