"""GitHub Trending data source collector.

Fetches trending repositories from GitHub's trending page
by parsing the HTML content.
"""

import re
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import SourceItem, SourceType
from .base import BaseSource


class GitHubSource(BaseSource):
    """Collector for GitHub Trending repositories.

    Scrapes the GitHub Trending page to extract information
    about trending repositories including name, description,
    language, stars, and forks.

    Attributes:
        name: Display name of the source.
        source_type: The SourceType enum value.
        base_url: GitHub trending page URL.
        description: Brief description of this source.
    """

    name = "GitHub Trending"
    source_type = SourceType.GITHUB
    base_url = "https://github.com/trending"
    description = "Trending repositories on GitHub"

    def fetch(self, limit: int = 20, since: str = "daily") -> List[SourceItem]:
        """Fetch trending repositories from GitHub.

        Args:
            limit: Maximum number of repositories to fetch.
            since: Time range - 'daily', 'weekly', or 'monthly'.

        Returns:
            List of SourceItem objects representing trending repos.
        """
        url = f"{self.base_url}?since={since}"
        html = self.client.get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # Find all repository article elements
        articles = soup.select("article.Box-row")
        if not articles:
            # Fallback: try older GitHub layout
            articles = soup.select("li.repo-list-item")
        if not articles:
            # Another fallback pattern
            articles = soup.select(".repo-list li")

        for article in articles[:limit]:
            try:
                item = self._parse_article(article)
                if item:
                    items.append(item)
            except Exception:
                # Skip malformed entries
                continue

        return items

    def _parse_article(self, article) -> Optional[SourceItem]:
        """Parse a single GitHub trending article element.

        Args:
            article: BeautifulSoup element for a repository.

        Returns:
            Parsed SourceItem or None if parsing fails.
        """
        # Repository name (e.g., "owner/repo")
        if not article:
            return None
        name_elem = article.select_one("h2 a") or article.select_one("h2 a")
        if not name_elem:
            return None

        repo_name = name_elem.get_text(strip=True).replace("\n", "").replace(" ", "")
        repo_url = urljoin("https://github.com", name_elem.get("href", ""))

        # Description
        desc_elem = article.select_one("p")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # Programming language
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.get_text(strip=True) if lang_elem else ""

        # Also try alternative language selector
        if not language:
            lang_elem = article.select_one("span[itemprop='programmingLanguage']")
            language = lang_elem.get_text(strip=True) if lang_elem else ""

        # Stars today
        stars_today = 0
        stars_today_elem = article.select_one(".float-sm-right")
        if stars_today_elem:
            stars_text = stars_today_elem.get_text(strip=True)
            match = re.search(r"([\d,]+)\s*stars\s*today", stars_text, re.IGNORECASE)
            if match:
                stars_today = int(match.group(1).replace(",", ""))

        # Total stars
        total_stars = 0
        stars_link = article.select_one("a[href$='/stargazers']")
        if stars_link:
            stars_text = stars_link.get_text(strip=True)
            total_stars = self._parse_number(stars_text)

        # Forks
        forks = 0
        forks_link = article.select_one("a[href$='/forks']")
        if forks_link:
            forks_text = forks_link.get_text(strip=True)
            forks = self._parse_number(forks_text)

        # Built by (contributors)
        built_by = []
        built_by_elems = article.select(".avatar-user")
        for elem in built_by_elems[:3]:
            built_by.append(elem.get("alt", "").replace("@", ""))

        return SourceItem(
            title=repo_name,
            url=repo_url,
            content=description,
            author=repo_name.split("/")[0] if "/" in repo_name else "",
            source=self.source_type,
            score=total_stars,
            comments=forks,
            extra={
                "language": language,
                "stars_today": stars_today,
                "total_stars": total_stars,
                "forks": forks,
                "built_by": built_by,
            },
        )

    def _parse_number(self, text: str) -> int:
        """Parse a number string that may contain k/m suffixes.

        Args:
            text: Number string like "1.2k" or "345".

        Returns:
            Parsed integer value.
        """
        text = text.strip().replace(",", "")
        if not text:
            return 0

        multipliers = {"k": 1000, "m": 1000000}
        suffix = text[-1].lower()

        if suffix in multipliers:
            try:
                return int(float(text[:-1]) * multipliers[suffix])
            except ValueError:
                return 0

        try:
            return int(text)
        except ValueError:
            return 0

    def search(self, keyword: str, limit: int = 10) -> List[SourceItem]:
        """Search GitHub repositories using the GitHub search page.

        Args:
            keyword: Search keyword.
            limit: Maximum number of results.

        Returns:
            List of matching SourceItem objects.
        """
        url = f"https://github.com/search?q={keyword}&type=repositories"
        html = self.client.get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items: List[SourceItem] = []

        # GitHub search results are in .repo-list-item elements
        repo_list = soup.select(".repo-list-item")
        if not repo_list:
            # Fallback selector
            repo_list = soup.select("li[data-testid='repo-list-item']")

        for repo in repo_list[:limit]:
            try:
                # Repo name and link
                name_link = repo.select_one("a.v-align-middle")
                if not name_link:
                    continue

                repo_name = name_link.get_text(strip=True)
                repo_url = urljoin("https://github.com", name_link.get("href", ""))

                # Description
                desc_elem = repo.select_one("p")
                description = desc_elem.get_text(strip=True) if desc_elem else ""

                # Language
                lang_elem = repo.select_one("[itemprop='programmingLanguage']")
                language = lang_elem.get_text(strip=True) if lang_elem else ""

                # Stars
                stars = 0
                stars_elem = repo.select_one("a[href$='/stargazers']")
                if stars_elem:
                    stars = self._parse_number(stars_elem.get_text(strip=True))

                # Forks
                forks = 0
                forks_elem = repo.select_one("a[href$='/forks']")
                if forks_elem:
                    forks = self._parse_number(forks_elem.get_text(strip=True))

                items.append(SourceItem(
                    title=repo_name,
                    url=repo_url,
                    content=description,
                    author=repo_name.split("/")[0] if "/" in repo_name else "",
                    source=self.source_type,
                    score=stars,
                    comments=forks,
                    extra={
                        "language": language,
                        "total_stars": stars,
                        "forks": forks,
                    },
                ))
            except Exception:
                continue

        return items
