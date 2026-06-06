"""Data source collectors package."""

from .base import BaseSource
from .github import GitHubSource
from .reddit import RedditSource
from .hackernews import HackerNewsSource
from .weibo import WeiboSource
from .zhihu import ZhihuSource
from .bilibili import BilibiliSource

# Registry of all available sources
SOURCE_REGISTRY: dict = {
    "github": GitHubSource,
    "reddit": RedditSource,
    "hackernews": HackerNewsSource,
    "weibo": WeiboSource,
    "zhihu": ZhihuSource,
    "bilibili": BilibiliSource,
}


def get_source(name: str) -> "BaseSource":
    """Get a source instance by name.

    Args:
        name: The source name (e.g., 'github', 'reddit').

    Returns:
        An instance of the requested source.

    Raises:
        ValueError: If the source name is not recognized.
    """
    if name not in SOURCE_REGISTRY:
        available = ", ".join(sorted(SOURCE_REGISTRY.keys()))
        raise ValueError(f"Unknown source '{name}'. Available sources: {available}")
    return SOURCE_REGISTRY[name]()


def get_all_sources() -> dict:
    """Get all registered source classes.

    Returns:
        Dictionary mapping source names to source classes.
    """
    return SOURCE_REGISTRY.copy()


__all__ = [
    "BaseSource",
    "GitHubSource",
    "RedditSource",
    "HackerNewsSource",
    "WeiboSource",
    "ZhihuSource",
    "BilibiliSource",
    "SOURCE_REGISTRY",
    "get_source",
    "get_all_sources",
]
