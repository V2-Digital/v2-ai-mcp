"""Unit tests for the summarizer module."""

from unittest.mock import MagicMock, patch

from src.v2_ai_mcp.summarizer import summarize


@patch('src.v2_ai_mcp.summarizer.OpenAI')
def test_summarize_success(mock_openai):
    """Test successful text summarization."""
    # Mock the OpenAI client and response
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test summary."

    mock_client.chat.completions.create.return_value = mock_response

    # Test the summarize function
    result = summarize("This is a long blog post content that needs to be summarized.")

    assert result == "This is a test summary."
    mock_client.chat.completions.create.assert_called_once()

    # Verify the API call parameters
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"
    assert call_args[1]["max_tokens"] == 500
    assert call_args[1]["temperature"] == 0.3
    assert len(call_args[1]["messages"]) == 2
    assert call_args[1]["messages"][0]["role"] == "system"
    assert call_args[1]["messages"][1]["role"] == "user"
    assert "summarize this blog post" in call_args[1]["messages"][1]["content"].lower()


@patch('src.v2_ai_mcp.summarizer.OpenAI')
def test_summarize_api_error(mock_openai):
    """Test handling of OpenAI API errors."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    # Mock an API exception
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    result = summarize("Test content")

    assert result == "Error generating summary: API Error"


@patch('src.v2_ai_mcp.summarizer.os.getenv')
@patch('src.v2_ai_mcp.summarizer.OpenAI')
def test_summarize_with_api_key(mock_openai, mock_getenv):
    """Test that API key is properly retrieved from environment."""
    mock_getenv.return_value = "test-api-key"
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Summary result."
    mock_client.chat.completions.create.return_value = mock_response

    result = summarize("Test content")

    mock_getenv.assert_called_once_with("OPENAI_API_KEY")
    mock_openai.assert_called_once_with(api_key="test-api-key")
    assert result == "Summary result."


@patch('src.v2_ai_mcp.summarizer.OpenAI')
def test_summarize_empty_content(mock_openai):
    """Test summarizing empty content."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "No content to summarize."
    mock_client.chat.completions.create.return_value = mock_response

    result = summarize("")

    assert result == "No content to summarize."
    mock_client.chat.completions.create.assert_called_once()
