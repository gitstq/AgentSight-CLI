"""Data models for AgentSight-CLI.

Defines the core data structures used across the application,
including source items, search results, and extraction outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SourceType(Enum):
    """Supported data source types."""
    GITHUB = "github"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    WEIBO = "weibo"
    ZHIHU = "zhihu"
    BILIBILI = "bilibili"


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"
    RAG = "rag"


@dataclass
class SourceItem:
    """A single item collected from a data source.

    Attributes:
        title: The title or headline of the item.
        url: The URL link to the original content.
        content: The main content or summary text.
        author: The author or creator of the item.
        source: The data source type this item came from.
        score: The score, upvotes, or popularity metric.
        comments: Number of comments or interactions.
        created_at: When the item was created (ISO format string).
        extra: Additional metadata specific to the source.
        raw_data: Raw data from the source for debugging.
    """
    title: str
    url: str
    content: str = ""
    author: str = ""
    source: SourceType = SourceType.GITHUB
    score: int = 0
    comments: int = 0
    created_at: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SourceItem to a dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "author": self.author,
            "source": self.source.value,
            "score": self.score,
            "comments": self.comments,
            "created_at": self.created_at,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceItem":
        """Create a SourceItem from a dictionary."""
        source_type = SourceType(data.get("source", "github"))
        return cls(
            title=data.get("title", ""),
            url=data.get("url", ""),
            content=data.get("content", ""),
            author=data.get("author", ""),
            source=source_type,
            score=data.get("score", 0),
            comments=data.get("comments", 0),
            created_at=data.get("created_at", ""),
            extra=data.get("extra", {}),
            raw_data=data.get("raw_data", {}),
        )


@dataclass
class SearchResult:
    """A search result from keyword search.

    Attributes:
        keyword: The search keyword used.
        items: List of matching SourceItem objects.
        total: Total number of results found.
        sources: Which sources were searched.
    """
    keyword: str
    items: List[SourceItem] = field(default_factory=list)
    total: int = 0
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the SearchResult to a dictionary."""
        return {
            "keyword": self.keyword,
            "total": self.total,
            "sources": self.sources,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class ExtractedContent:
    """Extracted content from a URL.

    Attributes:
        url: The URL that was extracted.
        title: The page title.
        content: The main content text.
        author: The author of the content.
        published_at: Publication date.
        metadata: Additional metadata extracted from the page.
        links: List of links found in the content.
        images: List of image URLs found in the content.
    """
    url: str
    title: str = ""
    content: str = ""
    author: str = ""
    published_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ExtractedContent to a dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "published_at": self.published_at,
            "metadata": self.metadata,
            "links": self.links,
            "images": self.images,
        }
