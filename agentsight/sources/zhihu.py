"""Zhihu Hot List data source collector.

Fetches the Zhihu hot list (知乎热榜) by parsing the
Zhihu hot list API endpoint.
"""

import json
import re
from typing import List, Optional
from urllib.parse import quote

from ..models import SourceItem, SourceType
from .base import BaseSource


class ZhihuSource(BaseSource):
    """Collector for Zhihu Hot List (知乎热榜).

    Fetches trending questions/topics from Zhihu's hot list
    using their internal API endpoint.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: Zhihu hot list API URL.
        description: Brief description of this source.
    """

    name = "Zhihu Hot List"
    source_type = SourceType.ZHIHU
    base_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
    description = "Hot topics from Zhihu (知乎热榜)"

    # Alternative endpoints
    FALLBACK_URL = "https://www.zhihu.com/hot"

    def fetch(self, limit: int = 20) -> List[SourceItem]:
        """Fetch Zhihu hot list topics.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects representing hot topics.
        """
        # Try the API endpoint first
        items = self._fetch_from_api(limit)
        if items:
            return items

        # Fallback to HTML parsing
        return self._fetch_from_html(limit)

    def _fetch_from_api(self, limit: int) -> List[SourceItem]:
        """Fetch hot list data from Zhihu API.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects.
        """
        params = {
            "limit": limit,
            "desktop": "true",
        }

        headers = {
            "Accept": "application/json",
            "Referer": "https://www.zhihu.com/hot",
            "X-Requested-With": "XMLHttpRequest",
        }

        data = self.client.get_json(self.base_url, params=params, headers=headers)
        if not data or not isinstance(data, dict):
            return []

        items: List[SourceItem] = []
        raw_items = data.get("data", [])
        if not raw_items:
            return []

        for item_data in raw_items[:limit]:
            try:
                target = item_data.get("target", {})
                if not target:
                    continue

                title = target.get("title", "") or target.get("excerpt", "")
                question_id = target.get("id", "")

                # Build the question URL
                question_url = f"https://www.zhihu.com/question/{question_id}"

                # Extract content/excerpt
                excerpt = target.get("excerpt", "") or ""

                # Author info
                author = ""
                detail = target.get("detail", "") or ""
                if detail:
                    # Try to extract author from detail text
                    author_match = re.search(r"(\S+)\s*的回答", detail)
                    if author_match:
                        author = author_match.group(1)

                # Hot value (heat index)
                heat_value = 0
                try:
                    heat_value = int(item_data.get("detail_text", "0").replace(",", ""))
                except (ValueError, TypeError):
                    pass

                # Alternative heat from the target
                if not heat_value:
                    try:
                        heat_value = int(target.get("heat", 0) or 0)
                    except (ValueError, TypeError):
                        pass

                # Answer count
                answer_count = 0
                try:
                    answer_count = int(target.get("answer_count", 0) or 0)
                except (ValueError, TypeError):
                    pass

                items.append(SourceItem(
                    title=title,
                    url=question_url,
                    content=excerpt,
                    author=author,
                    source=self.source_type,
                    score=heat_value,
                    comments=answer_count,
                    extra={
                        "question_id": question_id,
                        "answer_count": answer_count,
                        "follower_count": target.get("follower_count", 0),
                        "type": target.get("type", ""),
                    },
                ))
            except Exception:
                continue

        return items

    def _fetch_from_html(self, limit: int) -> List[SourceItem]:
        """Fetch hot list data by parsing the HTML page.

        Args:
            limit: Maximum number of topics to fetch.

        Returns:
            List of SourceItem objects.
        """
        from bs4 import BeautifulSoup

        html = self.client.get(self.FALLBACK_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # Zhihu hot list items
        hot_items = soup.select(".HotList-item")
        if not hot_items:
            # Fallback selector
            hot_items = soup.select("[data-zhihu-topstory-hot-item]")

        for item in hot_items[:limit]:
            try:
                # Title
                title_elem = item.select_one(".HotList-itemTitle") or item.select_one("h2")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Link
                link_elem = item.select_one("a[href*='/question/']") or item.select_one("a")
                if link_elem:
                    href = link_elem.get("href", "")
                    if href.startswith("/"):
                        item_url = f"https://www.zhihu.com{href}"
                    else:
                        item_url = href
                else:
                    continue

                # Hot value text
                hot_text = ""
                hot_elem = item.select_one(".HotList-itemMetrics") or item.select_one(".meta")
                if hot_elem:
                    hot_text = hot_elem.get_text(strip=True)

                # Extract number from hot text (e.g., "1234 万热度")
                heat_value = 0
                if hot_text:
                    match = re.search(r"([\d,]+)", hot_text)
                    if match:
                        heat_value = int(match.group(1).replace(",", ""))

                # Excerpt
                excerpt = ""
                excerpt_elem = item.select_one(".HotList-itemExcerpt") or item.select_one(".content")
                if excerpt_elem:
                    excerpt = excerpt_elem.get_text(strip=True)

                items.append(SourceItem(
                    title=title,
                    url=item_url,
                    content=excerpt,
                    author="",
                    source=self.source_type,
                    score=heat_value,
                    comments=0,
                    extra={
                        "hot_text": hot_text,
                    },
                ))
            except Exception:
                continue

        return items

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search Zhihu by keyword.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        # Use Zhihu search API
        search_url = "https://www.zhihu.com/api/v4/search_v3"
        params = {
            "t": "general",
            "q": keyword,
            "correction": 1,
            "offset": 0,
            "limit": limit,
            "filter_fields": "",
            "lc_idx": 0,
            "show_all_topics": 0,
        }

        headers = {
            "Accept": "application/json",
            "Referer": f"https://www.zhihu.com/search?type=content&q={quote(keyword)}",
        }

        data = self.client.get_json(search_url, params=params, headers=headers)
        if not data or not isinstance(data, dict):
            return []

        items: List[SourceItem] = []
        search_items = data.get("data", [])
        if not search_items:
            return []

        for search_item in search_items[:limit]:
            try:
                obj = search_item.get("object", {})
                if not obj:
                    continue

                item_type = search_item.get("type", "")
                highlight = search_item.get("highlight", "")

                title = obj.get("title", "") or obj.get("name", "")
                content = obj.get("excerpt", "") or obj.get("content", "") or ""

                # Build URL based on type
                if item_type == "search_result":
                    item_url = obj.get("url", "")
                    if not item_url:
                        question_id = obj.get("id", "")
                        item_url = f"https://www.zhihu.com/question/{question_id}"
                else:
                    item_url = obj.get("url", "")

                # Author
                author = ""
                author_info = obj.get("author", {})
                if isinstance(author_info, dict):
                    author = author_info.get("name", "")

                items.append(SourceItem(
                    title=title,
                    url=item_url,
                    content=content[:500],
                    author=author,
                    source=self.source_type,
                    score=0,
                    comments=0,
                    extra={
                        "type": item_type,
                        "highlight": highlight,
                    },
                ))
            except Exception:
                continue

        return items
