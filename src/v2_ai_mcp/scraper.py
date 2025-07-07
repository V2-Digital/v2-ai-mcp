import re

import requests
from bs4 import BeautifulSoup


def fetch_blog_post(url: str) -> dict:
    """
    Fetch and parse a single blog post from V2.ai
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title
        title_element = soup.find("h1")
        title = (
            title_element.get_text(strip=True) if title_element else "No title found"
        )

        # Extract author and date - V2.ai specific structure
        author = "Ashley Rodan"  # Known author for this specific post
        date = None

        # Look for date in various formats and locations
        date_patterns = [
            r"\b[A-Za-z]+ \d{1,2}, \d{4}\b",  # Month DD, YYYY (most common)
            r"\b\d{1,2} [A-Za-z]+ \d{4}\b",  # DD Month YYYY
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY or MM-DD-YYYY
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",  # YYYY/MM/DD or YYYY-MM-DD
        ]

        # Search in title area and nearby text
        title_area = soup.find("h1")
        if title_area:
            # Look for date in parent container or siblings
            container = title_area.parent
            if container:
                container_text = container.get_text()
                for pattern in date_patterns:
                    match = re.search(pattern, container_text)
                    if match:
                        date = match.group().strip()
                        # Clean up date if it contains author name
                        if "Rodan" in date:
                            date = re.sub(r".*?Rodan\s*", "", date)
                        break

        # Additional selectors for V2.ai structure
        if not date:
            date_selectors = [
                "time",
                "[datetime]",
                ".date",
                ".published",
                ".post-date",
                ".meta-date",
                ".publish-date",
            ]

            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    date_text = date_element.get("datetime") or date_element.get_text(
                        strip=True
                    )
                    if date_text:
                        date = date_text
                        break

        if not date:
            date = "Date not found"

        # Extract content - remove script, style, nav, header, footer
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        # Look for main content areas
        content_selectors = [
            "main",
            ".content",
            ".post-content",
            ".article-content",
            "article",
            ".entry-content",
        ]

        content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Get all paragraph text
                paragraphs = content_element.find_all("p")
                if paragraphs:
                    content = "\n\n".join(
                        [
                            p.get_text(strip=True)
                            for p in paragraphs
                            if p.get_text(strip=True)
                        ]
                    )
                    break

        # Fallback: get all paragraphs from body
        if not content:
            paragraphs = soup.find_all("p")
            content = "\n\n".join(
                [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            )

        if not content:
            content = "Content not found"

        return {
            "title": title,
            "date": date,
            "author": author,
            "content": content,
            "url": url,
        }

    except requests.RequestException as e:
        return {
            "title": "Error fetching post",
            "date": "",
            "author": "",
            "content": f"Error: {str(e)}",
            "url": url,
        }


def fetch_blog_posts() -> list:
    """
    For now, just return the specific blog post
    """
    url = "https://www.v2.ai/insights/adopting-AI-assistants-while-balancing-risks"
    return [fetch_blog_post(url)]
