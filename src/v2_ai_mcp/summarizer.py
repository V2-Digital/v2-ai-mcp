import os

from openai import OpenAI


def summarize(text: str) -> str:
    """
    Summarize the given text using OpenAI's GPT-4
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes blog posts. Provide a concise summary that captures the main points and key insights."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this blog post:\n\n{text}"
                }
            ],
            max_tokens=500,
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating summary: {str(e)}"
