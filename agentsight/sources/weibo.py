"""Weibo Hot Search data source collector.

Fetches the Weibo hot search trending topics by parsing
the Weibo hot search page or API endpoint.
"""

import json
import re
from typing import List, Optional

from bs4 import BeautifulSoup

from ..models import SourceItem, SourceType
from .base import BaseSource


class WeiboSource(BaseSource):
    """Collector for Weibo Hot Search (微博热搜).

    Fetches trending topics from Weibo's hot search page.
    Uses the mobile-friendly API endpoint for reliable data extraction.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: Weibo hot search URL.
        description: Brief description of this source.
    """

    name = "Weibo Hot Search"
    source_type = SourceType.WEIBO
    base_url = "https://s.weibo.com/top/summary"
    description = "Trending topics from Weibo (微博热搜)"

    # Alternative API endpoints
    API_URL = "https://weibo.com/ajax/side/hotSearch"
    FALLBACK_URL = "https://s.weibo.com/top/summary"

    def fetch(self, limit: int = 20) -> List[SourceItem]:
        """Fetch Weibo hot search trending topics.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects representing hot search topics.
        """
        # Try the AJAX API first (more reliable)
        items = self._fetch_from_api(limit)
        if items:
            return items

        # Fallback to HTML parsing
        return self._fetch_from_html(limit)

    def _fetch_from_api(self, limit: int) -> List[SourceItem]:
        """Fetch hot search data from Weibo AJAX API.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects.
        """
        headers = {
            "Accept": "application/json",
            "Referer": "https://weibo.com/",
            "X-Requested-With": "XMLHttpRequest",
        }

        data = self.client.get_json(self.API_URL, headers=headers, use_cache=True)
        if not data or not isinstance(data, dict):
            return []

        items: List[SourceItem] = []
        realtime = data.get("data", {}).get("realtime", [])
        if not realtime:
            return []

        for topic in realtime[:limit]:
            try:
                word = topic.get("word", "")
                if not word:
                    continue

                # Build the search URL for this topic
                encoded_word = word.replace("#", "").replace(" ", "")
                topic_url = f"https://s.weibo.com/weibo?q={encoded_word}"

                # Parse hot value (e.g., "1234567" or "123.4万")
                raw_hot = topic.get("raw_hot", 0) or 0
                label_name = topic.get("label_name", "")

                items.append(SourceItem(
                    title=word,
                    url=topic_url,
                    content=label_name,
                    author="",
                    source=self.source_type,
                    score=int(raw_hot) if isinstance(raw_hot, (int, float)) else 0,
                    comments=0,
                    extra={
                        "rank": topic.get("rank", 0),
                        "raw_hot": raw_hot,
                        "label_name": label_name,
                        "category": topic.get("category", ""),
                        "flag": topic.get("flag", ""),
                    },
                ))
            except Exception:
                continue

        return items

    def _fetch_from_html(self, limit: int) -> List[SourceItem]:
        """Fetch hot search data by parsing the HTML page.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects.
        """
        html = self.client.get(self.FALLBACK_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # Parse the hot search table
        rows = soup.select("tr[action-type='hover']")
        if not rows:
            # Fallback selector
            rows = soup.select("#pl_top_realtimehot table tbody tr")

        for row in rows[:limit]:
            try:
                # Topic title and link
                link_elem = row.select_one("td a")
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                href = link_elem.get("href", "")
                if href.startswith("/"):
                    topic_url = f"https://s.weibo.com{href}"
                else:
                    topic_url = href

                # Hot value (number)
                hot_value = 0
                hot_elem = row.select_one("td span")
                if hot_elem:
                    hot_text = hot_elem.get_text(strip=True)
                    hot_value = self._parse_hot_value(hot_text)

                # Rank
                rank = 0
                rank_elem = row.select_one("td:first-child")
                if rank_elem:
                    try:
                        rank = int(rank_elem.get_text(strip=True))
                    except ValueError:
                        rank = 0

                # Tag/label
                tag = ""
                tag_elem = row.select_one("td em") or row.select_one(".icon_hot")
                if tag_elem:
                    tag = tag_elem.get("title", "") or tag_elem.get_text(strip=True)

                items.append(SourceItem(
                    title=title,
                    url=topic_url,
                    content=tag,
                    author="",
                    source=self.source_type,
                    score=hot_value,
                    comments=0,
                    extra={
                        "rank": rank,
                        "tag": tag,
                    },
                ))
            except Exception:
                continue

        return items

    def _parse_hot_value(self, text: str) -> int:
        """Parse hot value text that may contain Chinese units.

        Args:
            text: Hot value text like "1234567" or "123.4万".

        Returns:
            Parsed integer value.
        """
        text = text.strip()
        if not text:
            return 0

        # Handle Chinese units
        if "万" in text:
            try:
                return int(float(text.replace("万", "")) * 10000)
            except ValueError:
                return 0
        elif "亿" in text:
            try:
                return int(float(text.replace("亿", "")) * 100000000)
            except ValueError:
                return 0

        # Plain number
        try:
            return int(text.replace(",", ""))
        except ValueError:
            return 0

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search Weibo by keyword.

        Since Weibo doesn't have a public search API, this method
        fetches the search page and parses results.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        from urllib.parse import quote
        url = f"https://s.weibo.com/weibo?q={quote(keyword)}"
        html = self.client.get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # Weibo search results are in .card-wrap elements
        cards = soup.select(".card-wrap[action-type='feed_list_item']")
        if not cards:
            cards = soup.select(".m-con-at")

        for card in cards[:limit]:
            try:
                # Title/content
                title_elem = card.select_one("p.txt a") or card.select_one(".txt a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")
                if href.startswith("/"):
                    post_url = f"https://weibo.com{href}"
                else:
                    post_url = href

                # Author
                author = ""
                author_elem = card.select_one(".name")
                if author_elem:
                    author = author_elem.get_text(strip=True)

                # Full text
                content = ""
                content_elem = card.select_one("p.txt")
                if content_elem:
                    content = content_elem.get_text(strip=True)

                items.append(SourceItem(
                    title=title[:100],
                    url=post_url,
                    content=content[:500],
                    author=author,
                    source=self.source_type,
                    score=0,
                    comments=0,
                ))
            except Exception:
                continue

        return items
