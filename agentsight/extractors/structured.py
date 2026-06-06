"""Structured data extractor.

Extracts structured data (JSON-LD, microdata, meta tags)
from web pages for RAG and LLM consumption.
"""

import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from ..models import ExtractedContent
from .base import BaseExtractor


class StructuredExtractor(BaseExtractor):
    """Extracts structured data from web pages.

    Focuses on extracting machine-readable structured data
    formats like JSON-LD, Open Graph, Twitter Cards, and
    microdata/microformats.

    Attributes:
        client: HTTP client instance.
        config: Configuration instance.
    """

    def extract(self, url: str) -> Optional[ExtractedContent]:
        """Extract structured data from a URL.

        Args:
            url: The URL to extract data from.

        Returns:
            ExtractedContent with structured metadata.
        """
        html = self.client.get(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # Extract all structured data
        json_ld = self._extract_json_ld(soup)
        open_graph = self._extract_open_graph(soup)
        twitter_card = self._extract_twitter_card(soup)
        meta_tags = self._extract_meta_tags(soup)
        microdata = self._extract_microdata(soup)

        # Build title
        title = open_graph.get("og:title", "") or meta_tags.get("title", "")

        # Build content from structured data
        content_parts = []
        if json_ld:
            content_parts.append(json.dumps(json_ld, ensure_ascii=False, indent=2))
        if open_graph:
            content_parts.append("Open Graph: " + json.dumps(open_graph, ensure_ascii=False, indent=2))
        if twitter_card:
            content_parts.append("Twitter Card: " + json.dumps(twitter_card, ensure_ascii=False, indent=2))

        content = "\n\n".join(content_parts)

        # Build metadata
        metadata: Dict[str, Any] = {
            "json_ld": json_ld,
            "open_graph": open_graph,
            "twitter_card": twitter_card,
            "meta_tags": meta_tags,
            "microdata": microdata,
        }

        # Extract links
        links = []
        seen = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            if href not in seen:
                seen.add(href)
                links.append(href)

        # Extract images
        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith("data:"):
                images.append(src)

        return ExtractedContent(
            url=url,
            title=title,
            content=content,
            author=open_graph.get("og:article:author", "") or meta_tags.get("author", ""),
            published_at=open_graph.get("og:article:published_time", "") or meta_tags.get("date", ""),
            metadata=metadata,
            links=links[:50],
            images=images[:20],
        )

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[List[Dict[str, Any]]]:
        """Extract JSON-LD structured data.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            List of JSON-LD objects, or None if none found.
        """
        results = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    results.extend(data)
                elif isinstance(data, dict):
                    results.append(data)
            except (json.JSONDecodeError, TypeError, AttributeError):
                continue

        return results if results else None

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph meta tags.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Dictionary of Open Graph properties.
        """
        og_data = {}
        for meta in soup.find_all("meta", attrs={"property": True}):
            prop = meta.get("property", "")
            if prop.startswith("og:") or prop.startswith("article:") or prop.startswith("profile:"):
                content = meta.get("content", "")
                if content:
                    og_data[prop] = content
        return og_data

    def _extract_twitter_card(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card meta tags.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Dictionary of Twitter Card properties.
        """
        twitter_data = {}
        for meta in soup.find_all("meta", attrs={"name": True}):
            name = meta.get("name", "")
            if name.startswith("twitter:"):
                content = meta.get("content", "")
                if content:
                    twitter_data[name] = content
        return twitter_data

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract standard HTML meta tags.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            Dictionary of meta tag properties.
        """
        meta_data = {}

        # Title
        title_tag = soup.find("title")
        if title_tag:
            meta_data["title"] = title_tag.get_text(strip=True)

        # Standard meta tags
        for meta in soup.find_all("meta", attrs={"name": True}):
            name = meta.get("name", "")
            content = meta.get("content", "")
            if name and content:
                meta_data[name] = content

        return meta_data

    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract microdata from itemscope elements.

        Args:
            soup: Parsed BeautifulSoup object.

        Returns:
            List of microdata item dictionaries.
        """
        results = []
        for item in soup.find_all(attrs={"itemscope": True}):
            item_type = item.get("itemtype", "")
            item_data = {"@type": item_type}

            # Extract itemprop values
            for prop in item.find_all(attrs={"itemprop": True}):
                prop_name = prop.get("itemprop", "")
                if prop.name == "meta":
                    prop_value = prop.get("content", "")
                elif prop.name == "link":
                    prop_value = prop.get("href", "")
                elif prop.name == "time":
                    prop_value = prop.get("datetime", "") or prop.get_text(strip=True)
                elif prop.name in ("img", "audio", "video", "source"):
                    prop_value = prop.get("src", "")
                elif prop.name == "a":
                    prop_value = prop.get("href", "") or prop.get_text(strip=True)
                else:
                    prop_value = prop.get_text(strip=True)

                if prop_value:
                    item_data[prop_name] = prop_value

            if len(item_data) > 1:  # More than just @type
                results.append(item_data)

        return results
