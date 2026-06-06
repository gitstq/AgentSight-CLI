"""Hacker News data source collector.

Fetches top stories from Hacker News using the official
Hacker News API (https://hacker-news.firebaseio.com).
"""

import re
from typing import List, Optional

from ..models import SourceItem, SourceType
from .base import BaseSource


class HackerNewsSource(BaseSource):
    """Collector for Hacker News stories.

    Uses the official Hacker News Firebase API to fetch
    top, new, and best stories with full metadata.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: Hacker News API base URL.
        description: Brief description of this source.
    """

    name = "Hacker News"
    source_type = SourceType.HACKERNEWS
    base_url = "https://hacker-news.firebaseio.com/v0"
    description = "Top stories from Hacker News"

    # Available story types
    STORY_TYPES = {
        "top": "topstories",
        "new": "newstories",
        "best": "beststories",
        "ask": "askstories",
        "show": "showstories",
        "job": "jobstories",
    }

    def fetch(self, limit: int = 20, story_type: str = "top") -> List[SourceItem]:
        """Fetch stories from Hacker News.

        Args:
            limit: Maximum number of stories to fetch.
            story_type: Type of stories - 'top', 'new', 'best', 'ask', 'show', 'job'.

        Returns:
            List of SourceItem objects representing HN stories.
        """
        endpoint = self.STORY_TYPES.get(story_type, "topstories")
        url = f"{self.base_url}/{endpoint}.json"

        story_ids = self.client.get_json(url)
        if not story_ids or not isinstance(story_ids, list):
            return []

        items: List[SourceItem] = []

        for story_id in story_ids[:limit]:
            try:
                item = self._fetch_story(story_id)
                if item:
                    items.append(item)
            except Exception:
                continue

        return items

    def _fetch_story(self, story_id: int) -> Optional[SourceItem]:
        """Fetch and parse a single Hacker News story.

        Args:
            story_id: The story ID from the API.

        Returns:
            Parsed SourceItem or None if fetching fails.
        """
        url = f"{self.base_url}/item/{story_id}.json"
        data = self.client.get_json(url)
        if not data or not isinstance(data, dict):
            return None

        # Skip deleted or dead items
        if data.get("deleted") or data.get("dead"):
            return None

        title = data.get("title", "")
        item_url = data.get("url", "")
        if not item_url:
            # Self-post (Ask HN, etc.), use HN comments page
            item_url = f"https://news.ycombinator.com/item?id={story_id}"

        # Convert Unix timestamp to ISO format
        timestamp = data.get("time", 0)
        created_at = ""
        if timestamp:
            from datetime import datetime, timezone
            created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        return SourceItem(
            title=title,
            url=item_url,
            content=data.get("text", "") or "",
            author=data.get("by", ""),
            source=self.source_type,
            score=data.get("score", 0),
            comments=data.get("descendants", 0),
            created_at=created_at,
            extra={
                "type": data.get("type", "story"),
                "hn_id": story_id,
                "hn_comments_url": f"https://news.ycombinator.com/item?id={story_id}",
            },
        )

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search Hacker News stories by keyword.

        Uses the Hacker News Algolia search API.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        # Use HN Search (Algolia) API
        search_url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": keyword,
            "tags": "story",
            "hitsPerPage": limit,
        }

        data = self.client.get_json(search_url, params=params)
        if not data or not isinstance(data, dict):
            return []

        hits = data.get("hits", [])
        items: List[SourceItem] = []

        for hit in hits:
            try:
                title = hit.get("title", "")
                item_url = hit.get("url", "")
                if not item_url:
                    object_id = hit.get("objectID", "")
                    item_url = f"https://news.ycombinator.com/item?id={object_id}"

                # Parse points
                points = 0
                try:
                    points = int(hit.get("points", 0) or 0)
                except (ValueError, TypeError):
                    points = 0

                # Parse comments count
                num_comments = 0
                try:
                    num_comments = int(hit.get("num_comments", 0) or 0)
                except (ValueError, TypeError):
                    num_comments = 0

                # Parse created_at
                created_at = hit.get("created_at", "")

                items.append(SourceItem(
                    title=title,
                    url=item_url,
                    content=hit.get("story_text", "") or "",
                    author=hit.get("author", ""),
                    source=self.source_type,
                    score=points,
                    comments=num_comments,
                    created_at=created_at,
                    extra={
                        "type": hit.get("story_text", "") and "comment" or "story",
                        "hn_id": hit.get("objectID", ""),
                    },
                ))
            except Exception:
                continue

        return items
