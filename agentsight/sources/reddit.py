"""Reddit data source collector.

Fetches popular posts from Reddit using the old.reddit.com interface
which provides server-rendered HTML that is easier to parse.
"""

import re
from typing import List, Optional
from urllib.parse import urljoin, quote

from bs4 import BeautifulSoup

from ..models import SourceItem, SourceType
from .base import BaseSource


class RedditSource(BaseSource):
    """Collector for Reddit posts.

    Uses the old.reddit.com HTML interface to fetch popular/trending
    posts from specified or default subreddits.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: Reddit old interface base URL.
        description: Brief description of this source.
    """

    name = "Reddit"
    source_type = SourceType.REDDIT
    base_url = "https://old.reddit.com"
    description = "Popular posts from Reddit"

    def fetch(self, limit: int = 20, subreddit: str = "") -> List[SourceItem]:
        """Fetch popular posts from Reddit.

        Args:
            limit: Maximum number of posts to fetch.
            subreddit: Subreddit name (empty for front page).

        Returns:
            List of SourceItem objects representing Reddit posts.
        """
        if subreddit:
            url = f"{self.base_url}/r/{subreddit}/"
        else:
            url = f"{self.base_url}/"

        html = self.client.get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # Reddit posts are in elements with id starting with "thing_t3_"
        posts = soup.select("#siteTable .thing[id^='thing_t3_']")
        if not posts:
            # Fallback selector
            posts = soup.select(".link")

        for post in posts[:limit]:
            try:
                item = self._parse_post(post)
                if item:
                    items.append(item)
            except Exception:
                continue

        return items

    def _parse_post(self, post) -> Optional[SourceItem]:
        """Parse a single Reddit post element.

        Args:
            post: BeautifulSoup element for a Reddit post.

        Returns:
            Parsed SourceItem or None if parsing fails.
        """
        # Title and URL
        if not post:
            return None
        title_elem = post.select_one("a.title") or post.select_one(".title a")
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)
        post_url = title_elem.get("href", "")

        # Make relative URLs absolute
        if post_url.startswith("/"):
            post_url = urljoin("https://www.reddit.com", post_url)

        # Comments link
        comments_elem = post.select_one(".comments")
        comments = 0
        if comments_elem:
            comments_text = comments_elem.get_text(strip=True)
            match = re.search(r"(\d+)\s*comments?", comments_text, re.IGNORECASE)
            if match:
                comments = int(match.group(1))

        # Score
        score = 0
        score_elem = post.select_one(".score.unvoted") or post.select_one(".score")
        if score_elem:
            score_text = score_elem.get("title", "") or score_elem.get_text(strip=True)
            try:
                score = int(score_text.replace(",", ""))
            except ValueError:
                score = 0

        # Author
        author = ""
        author_elem = post.select_one(".author")
        if author_elem:
            author = author_elem.get_text(strip=True)

        # Subreddit
        subreddit = ""
        sub_elem = post.select_one(".subreddit")
        if sub_elem:
            subreddit = sub_elem.get_text(strip=True)
        elif post.get("data-subreddit"):
            subreddit = post["data-subreddit"]

        # Post time
        time_elem = post.select_one("time")
        created_at = ""
        if time_elem:
            created_at = time_elem.get("datetime", "")

        # Thumbnail
        thumbnail = ""
        thumb_elem = post.select_one("a.thumbnail img") or post.select_one(".thumbnail img")
        if thumb_elem:
            thumbnail = thumb_elem.get("src", "")

        # Flair
        flair = ""
        flair_elem = post.select_one(".linkflairlabel")
        if flair_elem:
            flair = flair_elem.get_text(strip=True)

        return SourceItem(
            title=title,
            url=post_url,
            content="",
            author=author,
            source=self.source_type,
            score=score,
            comments=comments,
            created_at=created_at,
            extra={
                "subreddit": subreddit,
                "thumbnail": thumbnail,
                "flair": flair,
            },
        )

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search Reddit posts by keyword.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        encoded_keyword = quote(keyword)
        url = f"{self.base_url}/search?q={encoded_keyword}&sort=relevance&t=all"
        html = self.client.get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        posts = soup.select("#siteTable .thing[id^='thing_t3_']")
        if not posts:
            posts = soup.select(".link")

        for post in posts[:limit]:
            try:
                item = self._parse_post(post)
                if item:
                    items.append(item)
            except Exception:
                continue

        return items
