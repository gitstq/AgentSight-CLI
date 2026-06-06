"""HTML content extractor.

Extracts clean text content from HTML pages, removing
navigation, ads, and other boilerplate content.
"""

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment, NavigableString

from ..models import ExtractedContent
from .base import BaseExtractor


class HTMLExtractor(BaseExtractor):
    """Extracts main content from HTML pages.

    Uses heuristic-based content extraction to identify the main
    content area of a web page, removing navigation, sidebars,
    ads, and other boilerplate elements.

    Attributes:
        client: HTTP client instance.
        config: Configuration instance.
    """

    # Tags that are likely to contain boilerplate content
    BOILERPLATE_TAGS = {
        "nav", "header", "footer", "aside", "script", "style",
        "noscript", "iframe", "form", "button", "input",
        "select", "textarea", "svg", "canvas",
    }

    # CSS class/id patterns that indicate boilerplate
    BOILERPLATE_PATTERNS = re.compile(
        r"comment|sidebar|widget|footer|header|nav|menu|ad-|ads|banner|"
        r"social|share|related|recommend|promo|sponsor|popup|modal|"
        r"cookie|newsletter|subscribe|login|signup|register|search",
        re.IGNORECASE,
    )

    # CSS class/id patterns that indicate main content
    CONTENT_PATTERNS = re.compile(
        r"article|content|post|entry|story|body|main|text|"
        r"blog|news|description|abstract|summary",
        re.IGNORECASE,
    )

    def extract(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from a URL.

        Fetches the URL, parses the HTML, and extracts the main
        content along with metadata.

        Args:
            url: The URL to extract content from.

        Returns:
            ExtractedContent object if successful, None otherwise.
        """
        html = self.client.get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # Extract metadata
        title = self._extract_title(soup)
        author = self._extract_author(soup)
        published_at = self._extract_date(soup)
        description = self._extract_meta_description(soup)

        # Extract main content
        content = self._extract_main_content(soup)

        # If no main content found, fall back to body text
        if not content:
            content = self._extract_body_text(soup)

        # Extract links and images
        links = self._extract_links(soup, url)
        images = self._extract_images(soup, url)

        # Build metadata
        metadata = {
            "description": description,
            "word_count": len(content.split()) if content else 0,
            "char_count": len(content) if content else 0,
            "link_count": len(links),
            "image_count": len(images),
        }

        return ExtractedContent(
            url=url,
            title=title,
            content=content,
            author=author,
            published_at=published_at,
            metadata=metadata,
            links=links,
            images=images,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            The page title string.
        """
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Try title tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return ""

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract the author name.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            The author name string.
        """
        # Try meta author
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            return meta_author["content"].strip()

        # Try JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    author = data.get("author", {})
                    if isinstance(author, dict):
                        return author.get("name", "")
                    elif isinstance(author, str):
                        return author
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            author = item.get("author", {})
                            if isinstance(author, dict):
                                return author.get("name", "")
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue

        # Try common author selectors
        for selector in [".author", "[rel='author']", ".byline", ".post-author"]:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)

        return ""

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract the publication date.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            ISO format date string or empty string.
        """
        # Try various meta tags
        date_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "date"}),
            ("meta", {"name": "publish-date"}),
            ("meta", {"name": "DC.date.issued"}),
        ]

        for tag, attrs in date_selectors:
            elem = soup.find(tag, attrs)
            if elem and elem.get("content"):
                return elem["content"].strip()

        # Try time element
        time_elem = soup.find("time", attrs={"datetime": True})
        if time_elem:
            return time_elem["datetime"]

        return ""

    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract the meta description.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            The meta description string.
        """
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        return ""

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the page.

        Uses heuristic-based selection to find the main content area.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Extracted text content string.
        """
        # Try common content containers
        content_selectors = [
            "article",
            "[role='main']",
            "main",
            ".post-content",
            ".article-content",
            ".entry-content",
            ".content-body",
            ".story-body",
            "#content",
            "#article",
            "#main-content",
            ".main-content",
        ]

        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = self._clean_element(elem)
                if len(text) > 100:  # Minimum content length threshold
                    return text

        # If no specific content container found, try the largest text block
        return self._find_largest_text_block(soup)

    def _find_largest_text_block(self, soup: BeautifulSoup) -> str:
        """Find the largest block of text content in the page.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            The largest text block found.
        """
        # Remove boilerplate elements first
        cleaned = self._remove_boilerplate(soup)

        # Find the div or section with the most text
        candidates = cleaned.find_all(["div", "section", "main"])
        best_text = ""
        best_length = 0

        for elem in candidates:
            text = self._clean_element(elem)
            text_length = len(text)
            if text_length > best_length:
                best_length = text_length
                best_text = text

        return best_text

    def _remove_boilerplate(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove boilerplate elements from the soup.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Cleaned BeautifulSoup object.
        """
        # Clone the soup to avoid modifying the original
        cleaned = BeautifulSoup(str(soup), "lxml")

        # Remove script, style, and other boilerplate tags
        for tag in list(self.BOILERPLATE_TAGS):
            for elem in cleaned.find_all(tag):
                elem.decompose()

        # Remove elements with boilerplate class/id patterns
        for elem in cleaned.find_all(True):
            classes = " ".join(elem.get("class", []))
            elem_id = elem.get("id", "")
            if self.BOILERPLATE_PATTERNS.search(classes) or self.BOILERPLATE_PATTERNS.search(elem_id):
                elem.decompose()

        # Remove HTML comments
        for comment in cleaned.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        return cleaned

    def _clean_element(self, elem) -> str:
        """Extract clean text from an element.

        Args:
            elem: A BeautifulSoup element.

        Returns:
            Cleaned text string.
        """
        if elem is None:
            return ""

        # Get text with proper spacing
        text = elem.get_text(separator="\n", strip=True)

        # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        # Remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        """Extract text from the body as a fallback.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Body text string.
        """
        body = soup.find("body")
        if body:
            return self._clean_element(body)
        return soup.get_text(separator="\n", strip=True)

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract all links from the page.

        Args:
            soup: Parsed BeautifulSoup object.
            base_url: Base URL for resolving relative links.

        Returns:
            List of absolute URL strings.
        """
        links = []
        seen = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("#") or href.startswith("javascript:"):
                continue

            absolute_url = urljoin(base_url, href)
            if absolute_url not in seen:
                seen.add(absolute_url)
                links.append(absolute_url)

        return links[:50]  # Limit to 50 links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract all image URLs from the page.

        Args:
            soup: Parsed BeautifulSoup object.
            base_url: Base URL for resolving relative URLs.

        Returns:
            List of absolute image URL strings.
        """
        images = []
        seen = set()

        # Find img tags
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if src.startswith("data:"):
                continue

            absolute_url = urljoin(base_url, src)
            if absolute_url not in seen:
                seen.add(absolute_url)
                images.append(absolute_url)

        # Find og:image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            absolute_url = urljoin(base_url, og_image["content"])
            if absolute_url not in seen:
                images.append(absolute_url)

        return images[:20]  # Limit to 20 images
