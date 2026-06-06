"""Bilibili Hot Videos data source collector.

Fetches popular/trending videos from Bilibili (B站) by parsing
the Bilibili popular API endpoint.
"""

import json
import re
from typing import List, Optional
from urllib.parse import quote

from ..models import SourceItem, SourceType
from .base import BaseSource


class BilibiliSource(BaseSource):
    """Collector for Bilibili Hot Videos (B站热门).

    Fetches trending/popular videos from Bilibili's popular page
    using their API endpoint.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: Bilibili popular API URL.
        description: Brief description of this source.
    """

    name = "Bilibili Hot"
    source_type = SourceType.BILIBILI
    base_url = "https://api.bilibili.com/x/web-interface/popular"
    description = "Popular videos from Bilibili (B站热门)"

    # Additional endpoints
    RANKING_URL = "https://api.bilibili.com/x/web-interface/ranking/v2"
    SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"

    def fetch(self, limit: int = 20) -> List[SourceItem]:
        """Fetch popular videos from Bilibili.

        Args:
            limit: Maximum number of videos to fetch.

        Returns:
            List of SourceItem objects representing popular videos.
        """
        params = {
            "ps": limit,
            "pn": 1,
        }

        headers = {
            "Accept": "application/json",
            "Referer": "https://www.bilibili.com/v/popular/all",
        }

        data = self.client.get_json(self.base_url, params=params, headers=headers)
        if not data or not isinstance(data, dict):
            return []

        items: List[SourceItem] = []
        raw_list = data.get("data", {}).get("list", []) or data.get("data", {}).get("archives", [])
        if not raw_list:
            return []

        for video in raw_list[:limit]:
            try:
                item = self._parse_video(video)
                if item:
                    items.append(item)
            except Exception:
                continue

        return items

    def _parse_video(self, video: dict) -> Optional[SourceItem]:
        """Parse a single Bilibili video data dict.

        Args:
            video: Video data dictionary from the API.

        Returns:
            Parsed SourceItem or None if parsing fails.
        """
        title = video.get("title", "")
        if not title:
            return None

        bvid = video.get("bvid", "") or video.get("bvid", "")
        aid = video.get("aid", 0) or video.get("aid", 0)

        # Build video URL
        if bvid:
            video_url = f"https://www.bilibili.com/video/{bvid}"
        elif aid:
            video_url = f"https://www.bilibili.com/video/av{aid}"
        else:
            return None

        # Clean HTML entities from title
        title = self._clean_html(title)

        # Description
        desc = video.get("description", "") or video.get("desc", "")
        desc = self._clean_html(desc)

        # Author
        owner = video.get("owner", {}) or {}
        author = owner.get("name", "") or video.get("author", "") or ""

        # Stats
        stat = video.get("stat", {}) or {}
        play_count = self._parse_stat(stat.get("view", 0) or video.get("play", 0))
        danmaku_count = self._parse_stat(stat.get("danmaku", 0) or video.get("video_review", 0))
        like_count = self._parse_stat(stat.get("like", 0) or video.get("like", 0))
        coin_count = self._parse_stat(stat.get("coin", 0) or video.get("coins", 0))
        favorite_count = self._parse_stat(stat.get("favorite", 0) or video.get("favorite", 0))
        share_count = self._parse_stat(stat.get("share", 0) or video.get("share", 0))
        reply_count = self._parse_stat(stat.get("reply", 0) or video.get("reply", 0))

        # Duration
        duration = video.get("duration", "") or video.get("length", "")

        # Cover image
        pic = video.get("pic", "") or video.get("cover", "")

        # Category / Tname
        tname = video.get("tname", "") or ""
        rname = video.get("rname", "") or ""

        # Created timestamp
        created_at = ""
        pubdate = video.get("pubdate", 0) or video.get("pubdate", 0)
        if pubdate:
            from datetime import datetime, timezone
            created_at = datetime.fromtimestamp(int(pubdate), tz=timezone.utc).isoformat()

        return SourceItem(
            title=title,
            url=video_url,
            content=desc[:300],
            author=author,
            source=self.source_type,
            score=play_count,
            comments=reply_count,
            created_at=created_at,
            extra={
                "bvid": bvid,
                "aid": aid,
                "duration": duration,
                "cover": pic,
                "play_count": play_count,
                "danmaku_count": danmaku_count,
                "like_count": like_count,
                "coin_count": coin_count,
                "favorite_count": favorite_count,
                "share_count": share_count,
                "reply_count": reply_count,
                "category": tname or rname,
            },
        )

    def _parse_stat(self, value) -> int:
        """Parse a stat value that may be string or int.

        Args:
            value: The stat value (may be int, float, or string).

        Returns:
            Parsed integer value.
        """
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return 0
        return 0

    def _clean_html(self, text: str) -> str:
        """Remove HTML entities and tags from text.

        Args:
            text: Text that may contain HTML entities.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ""
        # Remove common HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&nbsp;", " ")
        # Remove any remaining HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search Bilibili videos by keyword.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        params = {
            "keyword": keyword,
            "search_type": "video",
            "page": 1,
            "page_size": limit,
        }

        headers = {
            "Accept": "application/json",
            "Referer": f"https://search.bilibili.com/all?keyword={quote(keyword)}",
        }

        data = self.client.get_json(self.SEARCH_URL, params=params, headers=headers)
        if not data or not isinstance(data, dict):
            return []

        items: List[SourceItem] = []
        result = data.get("data", {}) or {}
        results = result.get("result", []) or result.get("data", []) or []

        for video in results[:limit]:
            try:
                # Title may contain HTML tags
                title = video.get("title", "") or ""
                title = self._clean_html(title)

                if not title:
                    continue

                # Build URL
                bvid = video.get("bvid", "")
                arcurl = video.get("arcurl", "")
                if arcurl:
                    video_url = arcurl
                elif bvid:
                    video_url = f"https://www.bilibili.com/video/{bvid}"
                else:
                    continue

                # Author
                author = video.get("author", "") or ""
                if not author:
                    author_info = video.get("author", {})
                    if isinstance(author_info, dict):
                        author = author_info.get("name", "")

                # Description
                desc = video.get("description", "") or ""
                desc = self._clean_html(desc)

                # Stats
                play = self._parse_stat(video.get("play", 0))
                video_review = self._parse_stat(video.get("video_review", 0))
                favorites = self._parse_stat(video.get("favorites", 0))

                # Duration
                duration = video.get("duration", "") or ""

                # Cover
                pic = video.get("pic", "") or ""

                items.append(SourceItem(
                    title=title,
                    url=video_url,
                    content=desc[:300],
                    author=author,
                    source=self.source_type,
                    score=play,
                    comments=video_review,
                    extra={
                        "bvid": bvid,
                        "duration": duration,
                        "cover": pic,
                        "play_count": play,
                        "danmaku_count": video_review,
                        "favorite_count": favorites,
                    },
                ))
            except Exception:
                continue

        return items
